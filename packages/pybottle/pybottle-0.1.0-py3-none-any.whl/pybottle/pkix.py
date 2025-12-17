"""PKIX key serialization and parsing utilities."""

from typing import Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, x25519

from .errors import UnsupportedKeyTypeError

# Type aliases for supported key types
PublicKeyType = Union[
    rsa.RSAPublicKey,
    ec.EllipticCurvePublicKey,
    ed25519.Ed25519PublicKey,
    x25519.X25519PublicKey,
]

PrivateKeyType = Union[
    rsa.RSAPrivateKey,
    ec.EllipticCurvePrivateKey,
    ed25519.Ed25519PrivateKey,
    x25519.X25519PrivateKey,
]


def marshal_pkix_public_key(key: PublicKeyType) -> bytes:
    """
    Marshal a public key to PKIX/ASN.1 DER format.

    Args:
        key: A public key object

    Returns:
        The DER-encoded public key

    Raises:
        UnsupportedKeyTypeError: If the key type is not supported
    """
    try:
        return key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except Exception as e:
        raise UnsupportedKeyTypeError(f"Cannot marshal public key of type {type(key).__name__}: {e}")


def parse_pkix_public_key(der: bytes) -> PublicKeyType:
    """
    Parse a PKIX/ASN.1 DER-encoded public key.

    Args:
        der: The DER-encoded public key bytes

    Returns:
        A public key object

    Raises:
        UnsupportedKeyTypeError: If the key type is not supported
    """
    try:
        return serialization.load_der_public_key(der)
    except Exception as e:
        raise UnsupportedKeyTypeError(f"Cannot parse public key: {e}")


def get_public_key(private_key: PrivateKeyType) -> PublicKeyType:
    """
    Extract the public key from a private key.

    Args:
        private_key: A private key object

    Returns:
        The corresponding public key
    """
    return private_key.public_key()


def key_to_bytes(key: PublicKeyType | PrivateKeyType) -> bytes:
    """
    Convert a key to its PKIX DER representation.

    For private keys, this returns the public key bytes.

    Args:
        key: A public or private key

    Returns:
        The DER-encoded public key bytes
    """
    if hasattr(key, "public_key"):
        # It's a private key, get the public key
        key = key.public_key()
    return marshal_pkix_public_key(key)


def keys_equal(key1: PublicKeyType | bytes, key2: PublicKeyType | bytes) -> bool:
    """
    Check if two keys are equal.

    Args:
        key1: First key (public key object or DER bytes)
        key2: Second key (public key object or DER bytes)

    Returns:
        True if the keys are equal
    """
    if isinstance(key1, bytes):
        bytes1 = key1
    else:
        bytes1 = marshal_pkix_public_key(key1)

    if isinstance(key2, bytes):
        bytes2 = key2
    else:
        bytes2 = marshal_pkix_public_key(key2)

    return bytes1 == bytes2
