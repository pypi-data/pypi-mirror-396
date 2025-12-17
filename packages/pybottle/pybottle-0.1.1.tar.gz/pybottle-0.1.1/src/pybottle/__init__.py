"""
pybottle - Cryptographic message containers with signing and encryption.

A Python port of the Go cryptutil library, providing:
- Bottle: Signed, encrypted message containers
- IDCard: Identity cards linking signing keys to encryption keys
- Opener: For opening (decrypting/verifying) bottles
- Keychain: For managing private keys
"""

from .bottle import (
    Bottle,
    MessageFormat,
    MessageRecipient,
    MessageSignature,
    new_bottle,
    wrap,
    wrap_json,
    as_cbor_bottle,
    as_json_bottle,
)

from .opener import (
    Opener,
    OpenResult,
    new_opener,
    EMPTY_OPENER,
)

from .idcard import (
    IDCard,
    SubKey,
    new_idcard,
)

from .membership import (
    Membership,
    new_membership,
)

from .keychain import Keychain

from .errors import (
    CryptBottleError,
    NoAppropriateKeyError,
    VerifyFailedError,
    KeyNotFoundError,
    GroupNotFoundError,
    KeyUnfitError,
    EncryptNoRecipientError,
    UnsupportedKeyTypeError,
    DecryptionError,
    InvalidBottleError,
)

from .sign import sign, verify
from .pkix import encode_public_key, parse_pkix_public_key
from . import testkeys

__version__ = "0.1.1"

__all__ = [
    # Bottle
    "Bottle",
    "MessageFormat",
    "MessageRecipient",
    "MessageSignature",
    "new_bottle",
    "wrap",
    "wrap_json",
    "as_cbor_bottle",
    "as_json_bottle",
    # Opener
    "Opener",
    "OpenResult",
    "new_opener",
    "EMPTY_OPENER",
    # IDCard
    "IDCard",
    "SubKey",
    "new_idcard",
    # Membership
    "Membership",
    "new_membership",
    # Keychain
    "Keychain",
    # Errors
    "CryptBottleError",
    "NoAppropriateKeyError",
    "VerifyFailedError",
    "KeyNotFoundError",
    "GroupNotFoundError",
    "KeyUnfitError",
    "EncryptNoRecipientError",
    "UnsupportedKeyTypeError",
    "DecryptionError",
    "InvalidBottleError",
    # Utilities
    "sign",
    "verify",
    "encode_public_key",
    "parse_pkix_public_key",
    # Version
    "__version__",
    # Test keys
    "testkeys",
]
