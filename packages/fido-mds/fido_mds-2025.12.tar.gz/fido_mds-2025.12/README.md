# python-fido-mds

FIDO Alliance Metadata Service (MDS) in a Python package with WebAuthn attestation verification.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Overview

This package provides:

- **FIDO Metadata Service (MDS)** - Bundled and regularly updated FIDO Alliance authenticator metadata
- **Attestation Verification** - Comprehensive WebAuthn attestation format support
- **Type Safety** - Full Pydantic models for type-safe metadata and attestation handling
- **Production Ready** - Used in production environments for WebAuthn authentication

## Features

### FIDO Metadata Service

- Regularly updated authenticator metadata from FIDO Alliance
- Certificate chain verification
- Metadata statement validation
- Support for status reports

### Attestation Format Support

- ✅ **Android Key** - Complete KeyMint 4.0+ implementation with security validations

From python-fido2:
- ✅ **Packed** - Standard packed attestation format
- ✅ **TPM** - Trusted Platform Module attestation
- ✅ **Android SafetyNet** - Legacy Android attestation (via fido2 library)
- ✅ **Apple Anonymous** - Apple device attestation
- ✅ **FIDO U2F** - Universal 2nd Factor attestation
- ✅ **None** - Self attestation

## Installation

```bash
pip install fido-mds
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/SUNET/python-fido-mds.git
cd python-fido-mds

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Or using uv (faster)
uv pip install -e ".[dev]"

# Verify installation
pytest src
make reformat
make typecheck
```

This installs:
- All runtime dependencies (fido2, pydantic, cryptography, pyOpenSSL, asn1crypto)
- All development tools (pytest, pytest-cov, ruff, mypy)

## Quick Start

### Basic Attestation Verification

```python
from fido_mds import FidoMetadataStore
from fido_mds.models.webauthn import Attestation
from fido2.utils import websafe_decode

# Initialize metadata store
mds = FidoMetadataStore()

# Parse attestation object and client data
attestation = Attestation.from_base64(attestation_object_b64)
client_data = websafe_decode(client_data_b64)

# Verify attestation
try:
    result = mds.verify_attestation(attestation, client_data)
    print(f"✅ Attestation verified: {result}")
except Exception as e:
    print(f"❌ Verification failed: {e}")
```

### Android Key Attestation

```python
from fido_mds.models.attestation import AndroidKeyAttestation
import hashlib

# Create verifier
verifier = AndroidKeyAttestation()

# Prepare data
client_data_hash = hashlib.sha256(client_data).digest()

# Verify
result = verifier.verify(
    statement=attestation.attestation_obj.att_stmt,
    auth_data=attestation.attestation_obj.auth_data,
    client_data_hash=client_data_hash
)
```

## Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Comprehensive development guide including:
  - Setup and installation
  - Development workflow
  - Testing guidelines
  - Code quality standards
  - Architecture overview
  - **Special LLM section** for AI-assisted development

## Architecture

```
fido-mds/
├── models/
│   ├── attestation.py    # Attestation format implementations
│   ├── fido_mds.py       # FIDO MDS models
│   └── webauthn.py       # WebAuthn models
├── data/                 # Bundled metadata
├── tests/                # Test suite
│   ├── data.py          # Test attestation objects
│   └── test_*.py        # Test modules
├── helpers.py           # Utility functions
└── metadata_store.py    # Main API
```

## Requirements

- Python 3.10 or higher (tested with 3.13.3)
- fido2 >= 2.0.0
- pydantic >= 2.0
- cryptography
- pyOpenSSL
- asn1crypto (for Android Key attestation)

## Development

### Running Tests

```bash
# Activate virtualenv
source /path/to/virtualenv/bin/activate

# Run all tests
make test

# Run specific test
pytest src/fido_mds/tests/test_verify.py -v
```

### Code Quality

```bash
# Format code
make reformat

# Type checking
make typecheck

# Run all checks
make reformat && make typecheck && make test
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development guidelines.

## WebAuthn Specification Compliance

This package implements attestation verification according to:

- [WebAuthn Level 2 Specification](https://www.w3.org/TR/webauthn-2/)
- [Android Key Attestation](https://source.android.com/docs/security/features/keystore/attestation)
- [FIDO Metadata Service](https://fidoalliance.org/metadata/)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run all quality checks (`make reformat && make typecheck && make test`)
5. Submit a pull request

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed contribution guidelines.

## Testing

The test suite includes real attestation objects from various authenticators:

- **Android Key**: Google Pixel 8a, Samsung Tab S10+
- **FIDO U2F**: YubiKey 4/5
- **Packed**: YubiKey 5, Samsung Galaxy devices
- **Apple Anonymous**: iPhone, MacBook with Touch ID
- **TPM**: Windows Hello, Surface devices

All test data is sourced from actual WebAuthn registrations to ensure real-world compatibility.

### Test Coverage

```bash
# Run all tests
make test  # 15/15 passing

# Run specific test file
pytest src/fido_mds/tests/test_verify.py -v

# Test with coverage (optional, requires pytest-cov)
# pip install pytest-cov
# pytest src --cov=fido_mds --cov-report=html
```

## License

BSD 3-Clause License. See [LICENSE](LICENSE) file for details.

## Credits

- **Author**: Johan Lundberg (lundberg@sunet.se)
- **Organization**: SUNET
- **Repository**: https://github.com/SUNET/python-fido-mds

## References

- [WebAuthn Specification](https://www.w3.org/TR/webauthn-2/)
- [FIDO Alliance Metadata Service](https://fidoalliance.org/metadata/)
- [Android KeyStore Attestation](https://source.android.com/docs/security/features/keystore/attestation)
- [python-fido2 Library](https://github.com/Yubico/python-fido2)
- [duo-labs/py_webauthn](https://github.com/duo-labs/py_webauthn)

## Changelog

### October 2025

#### Complete Android Key Attestation Implementation
- ✅ **Full KeyDescription parsing** - Complete ASN.1 structure parsing with proper error handling
- ✅ **Origin validation** - Tag 702 (KM_ORIGIN_GENERATED) verification in hardwareEnforced
- ✅ **Purpose validation** - Tag 1 (KM_PURPOSE_SIGN) verification in hardwareEnforced
- ✅ **Security field validation** - Tag 600 (allApplications) rejection with correct DER encoding
- ✅ **Certificate chain validation** - Public key matching against Google Hardware Attestation roots
- ✅ **Full structure scanning** - Removed arbitrary byte limits, scans complete AuthorizationLists
- ✅ **WebAuthn compliance** - Follows WebAuthn Level 2 and Android Key Attestation specifications

#### Security Improvements
- 🔒 **Fixed allApplications detection** - Correct DER encoding (0xBF 0x84 0x58) instead of wrong pattern
- 🔒 **Public key matching** - Validates root certificates by public key, not just subject name
- 🔒 **Complete field scanning** - Removed dangerous [:50] and [:100] byte limits
- 🔒 **Certificate re-issuance handling** - Properly handles Google root certificate updates

#### Test Coverage
- ✅ Google Pixel 8a (Android Key attestation)
- ✅ Samsung Tab S10+ (Android Key attestation)
- ✅ YubiKey 4/5 (FIDO U2F and Packed)
- ✅ Apple devices (iPhone, MacBook)
- ✅ TPM attestation

#### Documentation
- ✅ Comprehensive DEVELOPMENT.md with LLM-specific guidelines
- ✅ Updated README with detailed Android Key attestation features
- ✅ Architecture documentation
- ✅ Security validation documentation

## Support

For issues, questions, or contributions:
- **Issues**: https://github.com/SUNET/python-fido-mds/issues
- **Email**: lundberg@sunet.se

---

**Note**: This package bundles FIDO Alliance metadata. Please ensure you comply with the FIDO Alliance Metadata Service Terms of Use.
