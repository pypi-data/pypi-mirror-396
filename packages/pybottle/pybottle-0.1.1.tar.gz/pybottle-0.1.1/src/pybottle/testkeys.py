"""Static test keys matching Go cryptutil test keys for interoperability testing."""

import base64

from cryptography.hazmat.primitives.serialization import load_der_private_key


def _b64decode(s: str) -> bytes:
    """Decode base64url without padding."""
    # Add padding if needed
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


# ECDSA P-256 keys (EC private key format)
_ALICE_DER = _b64decode("MHcCAQEEIIaSb1TJIeVordec4nMPaRBMsoroc462mpeWDuMEhY1-oAoGCCqGSM49AwEHoUQDQgAE09oIghTDnluvtv0-NKMhTS2nfC3TzR4DWnZK7czzFPZSH6bJN5oMZCp5X7pfI4BbIyTVtGeRKg6GTpzzfE-KYA")
_BOB_DER = _b64decode("MHcCAQEEIIPJmeofQddlqI3MNJEBcjEVhNjoR-aYpJXLa3X2q40koAoGCCqGSM49AwEHoUQDQgAEigRCfu95oGP9FNSLWoxhhCDEmgxYG8tMwlFItzAuV6W_fw0Og2BNG3yc0qOb-cEJjQKWRI9i_m1FUc97ajaTrg")

# Ed25519 keys (PKCS8 format)
_CHLOE_DER = _b64decode("MC4CAQAwBQYDK2VwBCIEIPFWBuWK8Ms8fdCdVogl7elV1H56AxiUHMsGl85l4NTB")
_DANIEL_DER = _b64decode("MC4CAQAwBQYDK2VwBCIEIMyPtgaGrXQ7VwAaZ-7cnwWQaAUpD4mQNzVo0-42CZ5V")


def get_alice():
    """Get Alice's ECDSA P-256 private key."""
    from cryptography.hazmat.primitives.serialization import load_der_private_key
    return load_der_private_key(_ALICE_DER, password=None)


def get_bob():
    """Get Bob's ECDSA P-256 private key."""
    from cryptography.hazmat.primitives.serialization import load_der_private_key
    return load_der_private_key(_BOB_DER, password=None)


def get_chloe():
    """Get Chloe's Ed25519 private key."""
    from cryptography.hazmat.primitives.serialization import load_der_private_key
    return load_der_private_key(_CHLOE_DER, password=None)


def get_daniel():
    """Get Daniel's Ed25519 private key."""
    from cryptography.hazmat.primitives.serialization import load_der_private_key
    return load_der_private_key(_DANIEL_DER, password=None)


# Lazy-loaded keys
alice = None
bob = None
chloe = None
daniel = None


def _init_keys():
    global alice, bob, chloe, daniel
    if alice is None:
        alice = get_alice()
        bob = get_bob()
        chloe = get_chloe()
        daniel = get_daniel()


def load_all():
    """Load all test keys."""
    _init_keys()
    return alice, bob, chloe, daniel
