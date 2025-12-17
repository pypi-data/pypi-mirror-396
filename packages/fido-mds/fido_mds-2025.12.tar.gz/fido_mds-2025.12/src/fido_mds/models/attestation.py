from logging import getLogger
from typing import Any, Mapping

from asn1crypto.core import Sequence as Asn1Sequence
from cryptography import x509
from cryptography.exceptions import InvalidSignature as _InvalidSignature
from cryptography.hazmat.backends import default_backend
from fido2.attestation import Attestation
from fido2.attestation.base import (
    AttestationResult,
    AttestationType,
    InvalidData,
    InvalidSignature,
    catch_builtins,
)
from fido2.cose import CoseKey
from fido2.webauthn import AuthenticatorData

__author__ = "lundberg"

logger = getLogger(__name__)


class AndroidKeyAttestation(Attestation):
    FORMAT: str = "android-key"

    @staticmethod
    def _validate_key_description(ext_value: bytes, client_data_hash: bytes) -> None:
        """
        Parse and validate Android Key attestation KeyDescription extension.

        KeyDescription ::= SEQUENCE {
            attestationVersion        INTEGER,        -- Value 400 (KeyMint 4.0)
            attestationSecurityLevel  SecurityLevel,  -- Software(0), TrustedEnvironment(1), StrongBox(2)
            keyMintVersion            INTEGER,        -- Value 400
            keyMintSecurityLevel      SecurityLevel,
            attestationChallenge      OCTET STRING,   -- Must match clientDataHash
            uniqueId                  OCTET STRING,
            softwareEnforced          AuthorizationList,
            hardwareEnforced          AuthorizationList,
        }

        Per WebAuthn spec (https://www.w3.org/TR/webauthn-2/#sctn-android-key-attestation):
        - attestationChallenge must be identical to clientDataHash
        - AuthorizationList must not contain allApplications field (would be tag 600)
        - For TEE keys: origin should be KM_ORIGIN_GENERATED (tag 702, value 0)
        - For TEE keys: purpose should contain KM_PURPOSE_SIGN (tag 1, value 2)

        Raises InvalidData if validation fails.
        """

        key_desc = Asn1Sequence.load(ext_value)

        if len(key_desc) < 8:
            raise InvalidData("Invalid KeyDescription structure")

        # Extract fields based on actual schema
        attestation_version = key_desc[0]  # INTEGER
        attestation_security_level = key_desc[1]  # SecurityLevel ENUMERATED
        keymint_version = key_desc[2]  # INTEGER
        keymint_security_level = key_desc[3]  # SecurityLevel ENUMERATED
        attestation_challenge = key_desc[4]  # OCTET STRING
        unique_id = key_desc[5]  # OCTET STRING
        software_enforced = key_desc[6]  # AuthorizationList SEQUENCE
        hardware_enforced = key_desc[7]  # AuthorizationList SEQUENCE (TEE or StrongBox)

        # Verify attestationChallenge matches clientDataHash
        challenge_bytes = bytes(attestation_challenge)
        if challenge_bytes != client_data_hash:
            raise InvalidData("Attestation challenge does not match client data hash")

        # Verify authorization lists per WebAuthn spec:
        # "The AuthorizationList.allApplications field is not present on either
        # authorization list (softwareEnforced nor teeEnforced), since
        # PublicKeyCredential MUST be scoped to the RP ID."
        #
        # Note: allApplications would have tag 600, but it's not in the standard schema.
        # This was likely from an older version. Modern implementations should not have it.
        # We check both lists as a safety measure.
        for auth_list_name, auth_list in [
            ("softwareEnforced", software_enforced),
            ("hardwareEnforced", hardware_enforced),
        ]:
            try:
                auth_list_bytes = auth_list.dump()
                # Tag 600 (allApplications) is encoded as 0xBF 0x84 0x58 in DER
                # Context-specific, constructed, high tag number form
                # This field should NOT be present in secure attestations
                if b"\xbf\x84\x58" in auth_list_bytes:
                    logger.error(f"allApplications field found in {auth_list_name}")
                    raise InvalidData(f"AuthorizationList.allApplications found in {auth_list_name}")
            except (ValueError, TypeError, AttributeError) as e:
                # Handle ASN.1 serialization errors
                logger.debug(f"Could not validate {auth_list_name}: {e}")
                raise InvalidData(f"AuthorizationList.allApplications check failed")

        # Verify origin field (tag 702) in hardwareEnforced
        # Per WebAuthn spec: origin should be KM_ORIGIN_GENERATED (0)
        # Tag 702 in DER with context-specific encoding: 0xBF 0x85 0x3E
        hw_enforced_bytes = hardware_enforced.dump()

        origin_tag = b"\xbf\x85>"  # Tag 702 encoded (0xBF 0x85 0x3E)
        if origin_tag not in hw_enforced_bytes:
            logger.error("Origin field (tag 702) not found in hardwareEnforced authorization list")
            raise InvalidData(f"Origin field check failed")
        logger.debug("Found origin field (tag 702) in hardwareEnforced")

        # Verify purpose field (tag 1) in hardwareEnforced
        # Per WebAuthn spec: purpose should contain KM_PURPOSE_SIGN (2)
        # Tag 1 in DER with context-specific encoding: 0xA1
        purpose_tag = b"\xa1"  # Tag 1 encoded
        if purpose_tag not in hw_enforced_bytes:
            logger.error("Purpose field (tag 1) not found in hardwareEnforced authorization list")
            raise InvalidData(f"Purpose field check failed")
        logger.debug("Found purpose field (tag 1) in hardwareEnforced")

    @catch_builtins
    def verify(
        self,
        statement: Mapping[str, Any],
        auth_data: AuthenticatorData,
        client_data_hash: bytes,
    ) -> AttestationResult:
        """
        Verify Android Key attestation according to:
        https://www.w3.org/TR/webauthn-2/#sctn-android-key-attestation
        https://source.android.com/docs/security/features/keystore/attestation
        """
        alg = statement.get("alg")
        if not alg:
            raise InvalidData("Missing 'alg' in attestation statement")

        x5c = statement.get("x5c")
        if not x5c or len(x5c) == 0:
            raise InvalidData("Missing 'x5c' in attestation statement")

        sig = statement.get("sig")
        if not sig:
            raise InvalidData("Missing 'sig' in attestation statement")

        # Load the attestation certificate
        cert = x509.load_der_x509_certificate(x5c[0], default_backend())

        # Verify that sig is a valid signature over the concatenation of
        # authenticatorData and clientDataHash using the public key in the
        # first certificate in x5c with the algorithm specified in alg
        cose_key = CoseKey.for_alg(alg).from_cryptography_key(cert.public_key())
        att_to_be_signed = auth_data + client_data_hash

        try:
            cose_key.verify(att_to_be_signed, sig)
        except _InvalidSignature:
            logger.exception("Failed to verify attestation signature")
            raise InvalidSignature("Signature verification failed")

        # Verify that the public key in the first certificate matches the
        # credentialPublicKey in the attestedCredentialData
        if not auth_data.credential_data:
            raise InvalidData("Missing credential data in authenticator data")

        cred_pub_key = auth_data.credential_data.public_key

        if cose_key != cred_pub_key:
            raise InvalidData("Certificate public key does not match credential public key")

        # Verify the attestation certificate extension data
        # OID for Key Description extension: 1.3.6.1.4.1.11129.2.1.17
        ext_oid = x509.ObjectIdentifier("1.3.6.1.4.1.11129.2.1.17")
        try:
            ext = cert.extensions.get_extension_for_oid(ext_oid)
        except x509.ExtensionNotFound:
            raise InvalidData(f"Certificate missing Android Key attestation extension {ext_oid}")

        # Parse the extension value
        # The extension value is ASN.1 DER encoded KeyDescription
        # Get the raw bytes from the UnrecognizedExtension
        if isinstance(ext.value, x509.UnrecognizedExtension):
            ext_value = ext.value.value
        else:
            raise InvalidData("Unexpected extension type")

        self._validate_key_description(ext_value, client_data_hash)

        return AttestationResult(AttestationType.BASIC, x5c or [])
