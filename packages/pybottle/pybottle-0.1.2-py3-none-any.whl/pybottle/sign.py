"""Signing and verification functions."""

import hashlib
from typing import Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, padding
from cryptography.exceptions import InvalidSignature

from .errors import VerifyFailedError, UnsupportedKeyTypeError
from .pkix import PrivateKeyType, PublicKeyType

# Type for signing keys
SigningKeyType = Union[
    rsa.RSAPrivateKey,
    ec.EllipticCurvePrivateKey,
    ed25519.Ed25519PrivateKey,
]

# Type for verification keys
VerifyKeyType = Union[
    rsa.RSAPublicKey,
    ec.EllipticCurvePublicKey,
    ed25519.Ed25519PublicKey,
]


def sign(
    private_key: SigningKeyType,
    data: bytes,
    hash_algorithm: hashes.HashAlgorithm | None = None,
    use_pss: bool = False,
) -> bytes:
    """
    Sign data using the given private key.

    Unlike standard library sign methods, this takes the raw data
    and performs hashing internally as needed.

    Args:
        private_key: The private key to sign with
        data: The data to sign
        hash_algorithm: Hash algorithm to use (default: SHA256)
        use_pss: Use PSS padding for RSA (default: False, uses PKCS1v15)

    Returns:
        The signature bytes

    Raises:
        UnsupportedKeyTypeError: If the key type is not supported
    """
    if hash_algorithm is None:
        hash_algorithm = hashes.SHA256()

    match private_key:
        case rsa.RSAPrivateKey():
            if use_pss:
                pad = padding.PSS(
                    mgf=padding.MGF1(hash_algorithm),
                    salt_length=padding.PSS.AUTO,
                )
            else:
                pad = padding.PKCS1v15()
            return private_key.sign(data, pad, hash_algorithm)

        case ec.EllipticCurvePrivateKey():
            return private_key.sign(data, ec.ECDSA(hash_algorithm))

        case ed25519.Ed25519PrivateKey():
            # Ed25519 doesn't use a separate hash - it's built into the algorithm
            return private_key.sign(data)

        case _:
            raise UnsupportedKeyTypeError(f"Cannot sign with key type {type(private_key).__name__}")


def verify(
    public_key: VerifyKeyType,
    data: bytes,
    signature: bytes,
    hash_algorithm: hashes.HashAlgorithm | None = None,
    use_pss: bool = False,
) -> None:
    """
    Verify a signature against data using the given public key.

    Args:
        public_key: The public key to verify with
        data: The original data that was signed
        signature: The signature to verify
        hash_algorithm: Hash algorithm used (default: SHA256)
        use_pss: Use PSS padding for RSA (default: False)

    Raises:
        VerifyFailedError: If signature verification fails
        UnsupportedKeyTypeError: If the key type is not supported
    """
    if hash_algorithm is None:
        hash_algorithm = hashes.SHA256()

    try:
        match public_key:
            case rsa.RSAPublicKey():
                if use_pss:
                    pad = padding.PSS(
                        mgf=padding.MGF1(hash_algorithm),
                        salt_length=padding.PSS.AUTO,
                    )
                else:
                    pad = padding.PKCS1v15()
                public_key.verify(signature, data, pad, hash_algorithm)

            case ec.EllipticCurvePublicKey():
                public_key.verify(signature, data, ec.ECDSA(hash_algorithm))

            case ed25519.Ed25519PublicKey():
                public_key.verify(signature, data)

            case _:
                raise UnsupportedKeyTypeError(f"Cannot verify with key type {type(public_key).__name__}")

    except InvalidSignature:
        raise VerifyFailedError("Signature verification failed")
