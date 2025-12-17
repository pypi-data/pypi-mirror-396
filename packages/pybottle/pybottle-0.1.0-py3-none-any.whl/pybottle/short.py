"""Short buffer encryption/decryption with key type routing."""

import hashlib
from typing import Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, x25519, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .errors import UnsupportedKeyTypeError, DecryptionError
from .ecdh import ecdh_encrypt, ecdh_decrypt, ECDHPublicKeyType, ECDHPrivateKeyType
from .utils import hash_data, memclr

# Type aliases
EncryptionPublicKeyType = Union[
    rsa.RSAPublicKey,
    ec.EllipticCurvePublicKey,
    ed25519.Ed25519PublicKey,
    x25519.X25519PublicKey,
]

DecryptionPrivateKeyType = Union[
    rsa.RSAPrivateKey,
    ec.EllipticCurvePrivateKey,
    ed25519.Ed25519PrivateKey,
    x25519.X25519PrivateKey,
]


def _ed25519_public_to_x25519(ed_public: ed25519.Ed25519PublicKey) -> x25519.X25519PublicKey:
    """
    Convert an Ed25519 public key to an X25519 public key.

    This uses the birational map between the Edwards curve (Ed25519)
    and the Montgomery curve (Curve25519/X25519):
    u = (1 + y) / (1 - y)

    where y is the y-coordinate of the Ed25519 point.
    """
    # Get the raw bytes of the Ed25519 public key (32 bytes, compressed Edwards point)
    ed_bytes = ed_public.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )

    # The Ed25519 public key is the y-coordinate with the sign of x in the high bit
    # We need to convert from Edwards y to Montgomery u
    # u = (1 + y) / (1 - y) mod p
    # where p = 2^255 - 19

    p = 2**255 - 19

    # Decode y from little-endian bytes (clear the high bit which is the sign)
    y = int.from_bytes(ed_bytes, 'little')
    y &= (1 << 255) - 1  # Clear the high bit

    # Compute u = (1 + y) / (1 - y) mod p
    # Using Fermat's little theorem: a^(-1) = a^(p-2) mod p
    numerator = (1 + y) % p
    denominator = (1 - y) % p
    denominator_inv = pow(denominator, p - 2, p)
    u = (numerator * denominator_inv) % p

    # Encode u as 32 bytes little-endian
    u_bytes = u.to_bytes(32, 'little')

    return x25519.X25519PublicKey.from_public_bytes(u_bytes)


def _ed25519_private_to_x25519(ed_private: ed25519.Ed25519PrivateKey) -> x25519.X25519PrivateKey:
    """
    Convert an Ed25519 private key to an X25519 private key.

    The X25519 private key is derived from the Ed25519 seed by hashing
    with SHA-512 and taking the first 32 bytes with clamping.
    """
    # Get the seed (32 bytes)
    ed_bytes = ed_private.private_bytes(
        encoding=Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    # Ed25519 private bytes in Raw format is the seed (32 bytes)
    seed = ed_bytes[:32]

    # Hash with SHA-512
    digest = bytearray(hashlib.sha512(seed).digest())

    try:
        # Apply clamping to first 32 bytes (same as Ed25519 scalar derivation)
        digest[0] &= 248
        digest[31] &= 127
        digest[31] |= 64

        # Use the first 32 bytes as the X25519 private key
        return x25519.X25519PrivateKey.from_private_bytes(bytes(digest[:32]))
    finally:
        memclr(digest)


# Need this import for _ed25519_private_to_x25519
from cryptography.hazmat.primitives import serialization


def encrypt_short_buffer(data: bytes, public_key: EncryptionPublicKeyType) -> bytes:
    """
    Encrypt a short buffer (like a key) for a recipient.

    Handles routing to the appropriate encryption method based on key type:
    - RSA: RSA-OAEP with SHA256
    - ECDSA/EC: Convert to ECDH and use ECDH encryption
    - Ed25519: Convert to X25519 and use ECDH encryption
    - X25519: Direct ECDH encryption

    Args:
        data: The data to encrypt (should be short, e.g., a symmetric key)
        public_key: The recipient's public key

    Returns:
        The encrypted data

    Raises:
        UnsupportedKeyTypeError: If the key type is not supported
    """
    match public_key:
        case rsa.RSAPublicKey():
            return public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                )
            )

        case ec.EllipticCurvePublicKey():
            # Use ECDH encryption
            return ecdh_encrypt(data, public_key)

        case ed25519.Ed25519PublicKey():
            # Convert to X25519 and use ECDH encryption
            x25519_public = _ed25519_public_to_x25519(public_key)
            return ecdh_encrypt(data, x25519_public)

        case x25519.X25519PublicKey():
            return ecdh_encrypt(data, public_key)

        case _:
            raise UnsupportedKeyTypeError(f"Unsupported public key type: {type(public_key).__name__}")


def decrypt_short_buffer(data: bytes, private_key: DecryptionPrivateKeyType) -> bytes:
    """
    Decrypt a short buffer that was encrypted for us.

    Handles routing to the appropriate decryption method based on key type:
    - RSA: RSA-OAEP with SHA256
    - ECDSA/EC: Use ECDH decryption
    - Ed25519: Convert to X25519 and use ECDH decryption
    - X25519: Direct ECDH decryption

    Args:
        data: The encrypted data
        private_key: The recipient's private key

    Returns:
        The decrypted data

    Raises:
        DecryptionError: If decryption fails
        UnsupportedKeyTypeError: If the key type is not supported
    """
    match private_key:
        case rsa.RSAPrivateKey():
            try:
                return private_key.decrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    )
                )
            except Exception as e:
                raise DecryptionError(f"RSA decryption failed: {e}")

        case ec.EllipticCurvePrivateKey():
            return ecdh_decrypt(data, private_key)

        case ed25519.Ed25519PrivateKey():
            # Convert to X25519 and use ECDH decryption
            x25519_private = _ed25519_private_to_x25519(private_key)
            return ecdh_decrypt(data, x25519_private)

        case x25519.X25519PrivateKey():
            return ecdh_decrypt(data, private_key)

        case _:
            raise UnsupportedKeyTypeError(f"Unsupported private key type: {type(private_key).__name__}")
