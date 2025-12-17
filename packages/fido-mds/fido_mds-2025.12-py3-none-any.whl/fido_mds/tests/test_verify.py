# -*- coding: utf-8 -*-

import pytest
from fido2.utils import websafe_decode
from fido2.webauthn import RegistrationResponse

from fido_mds.exceptions import MetadataValidationError
from fido_mds.metadata_store import FidoMetadataStore
from fido_mds.models.webauthn import Attestation
from fido_mds.tests.data import (
    IPHONE_12,
    MICROSOFT_SURFACE_1796,
    NEXUS_5,
    PIXEL_8A,
    YUBIKEY_4,
    YUBIKEY_5_NFC,
)

__author__ = "lundberg"


@pytest.mark.parametrize(
    "attestation_obj,client_data",
    [YUBIKEY_4, YUBIKEY_5_NFC, MICROSOFT_SURFACE_1796],
)
def test_verify(mds: FidoMetadataStore, attestation_obj: str, client_data: str):
    att = Attestation.from_base64(attestation_obj)
    cd = websafe_decode(client_data)
    assert mds.verify_attestation(attestation=att, client_data=cd) is True


def test_verify_registration_response(mds: FidoMetadataStore):
    data = {
        "response": {
            "authenticatorAttachment": "cross-platform",
            "clientExtensionResults": {},
            "id": "66W8fnwrLAXn-FgwE6W3GMtW8qEQzwUdL_Bz8adUzv_4sp6S7KCbsaYeIYaFoPbDjlEHxuqXUuDa2Gu1euuCKA",
            "rawId": "66W8fnwrLAXn-FgwE6W3GMtW8qEQzwUdL_Bz8adUzv_4sp6S7KCbsaYeIYaFoPbDjlEHxuqXUuDa2Gu1euuCKA",
            "response": {
                "attestationObject": "o2NmbXRoZmlkby11MmZnYXR0U3RtdKJjc2lnWEcwRQIgBGNHLKyOe-H9bq-iwfusMDQXrvrs0aMuRvXRMWnxQIkCIQDBwKkOup45cORs6-w_NHy1j4aBnOUOOYZbxQoZj_gZ3WN4NWOBWQIzMIICLzCCARmgAwIBAgIEQvUaTTALBgkqhkiG9w0BAQswLjEsMCoGA1UEAxMjWXViaWNvIFUyRiBSb290IENBIFNlcmlhbCA0NTcyMDA2MzEwIBcNMTQwODAxMDAwMDAwWhgPMjA1MDA5MDQwMDAwMDBaMCoxKDAmBgNVBAMMH1l1YmljbyBVMkYgRUUgU2VyaWFsIDExMjMzNTkzMDkwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAAQphQ-PJYiZjZEVHtrx5QGE3_LE1-OytZPTwzrpWBKywji_3qmg22mwmVFl32PO269TxY-yVN4jbfVf5uX0EWJWoyYwJDAiBgkrBgEEAYLECgIEFTEuMy42LjEuNC4xLjQxNDgyLjEuNDALBgkqhkiG9w0BAQsDggEBALSc3YwTRbLwXhePj_imdBOhWiqh6ssS2ONgp5tphJCHR5Agjg2VstLBRsJzyJnLgy7bGZ0QbPOyh_J0hsvgBfvjByXOu1AwCW-tcoJ-pfxESojDLDn8hrFph6eWZoCtBsWMDh6vMqPENeP6grEAECWx4fTpBL9Bm7F-0Rp_d1_l66g4IhF_ZvuRFhY-BUK94BfivuBHpEkMwxKENTas7VkxvlVstUvPqhPHGYOq7RdF1D_THsbNY8-tgCTgvTziEG-bfDeY6zIz5h7bxb1rpajNVTpUDWtVYL7_w44e1KCoErqdS-kEbmmkmm7KvDE8kuyg42Fmb5DTMsbY2jxMlMVoYXV0aERhdGFYxNz3BHEmKmoM4iTRAmMUgSjEdNSeKZskhyDzwzPuNmHTQQAAAAAAAAAAAAAAAAAAAAAAAAAAAEDrpbx-fCssBef4WDATpbcYy1byoRDPBR0v8HPxp1TO__iynpLsoJuxph4hhoWg9sOOUQfG6pdS4NrYa7V664IopQECAyYgASFYIDCQ34xF16zcYaMyrY03IfTzPUuZe1AuH9iGaqwibkMmIlgg0-euFQvCSRv1sK4M5UmCBNiUwHs3Zj3d4sVRLXrmWRc",
                "authenticatorData": "3PcEcSYqagziJNECYxSBKMR01J4pmySHIPPDM-42YdNBAAAAAAAAAAAAAAAAAAAAAAAAAAAAQOulvH58KywF5_hYMBOltxjLVvKhEM8FHS_wc_GnVM7_-LKekuygm7GmHiGGhaD2w45RB8bql1Lg2thrtXrrgiilAQIDJiABIVggMJDfjEXXrNxhozKtjTch9PM9S5l7UC4f2IZqrCJuQyYiWCDT564VC8JJG_WwrgzlSYIE2JTAezdmPd3ixVEteuZZFw",
                "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiNGdlU25QMHhqd3R0Ukh0ZjdmZm04ZVlTM3h6aUxfWUlfN0RmSVNRTThsRSIsIm9yaWdpbiI6Imh0dHBzOi8vaHRtbC5lZHVpZC5kb2NrZXIiLCJjcm9zc09yaWdpbiI6ZmFsc2V9",
                "publicKey": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEMJDfjEXXrNxhozKtjTch9PM9S5l7UC4f2IZqrCJuQybT564VC8JJG_WwrgzlSYIE2JTAezdmPd3ixVEteuZZFw",
                "publicKeyAlgorithm": -7,
                "transports": [],
            },
            "type": "public-key",
        },
        "description": "test",
    }
    registration = RegistrationResponse.from_dict(data["response"])
    att = Attestation.from_attestation_object(registration.response.attestation_object)
    assert mds.verify_attestation(attestation=att, client_data=registration.response.client_data) is True


# test attestations with short-lived certs so metadata can't be validated
@pytest.mark.parametrize("attestation_obj,client_data", [IPHONE_12, NEXUS_5, PIXEL_8A])
def test_verify_no_validate(mds: FidoMetadataStore, attestation_obj: str, client_data: str):
    att = Attestation.from_base64(attestation_obj)
    cd = websafe_decode(client_data)
    with pytest.raises(MetadataValidationError):
        mds.verify_attestation(attestation=att, client_data=cd)
