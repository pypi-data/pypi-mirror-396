"""ECDH encryption and decryption functions."""

import hashlib
import io
import os
from typing import Protocol, Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec, x25519

from .errors import DecryptionError, UnsupportedKeyTypeError
from .pkix import marshal_pkix_public_key, parse_pkix_public_key
from .utils import hash_data, memclr


class ECDHHandler(Protocol):
    """Protocol for objects that can perform ECDH key exchange."""

    def exchange(self, peer_public_key) -> bytes:
        """Perform ECDH key exchange and return shared secret."""
        ...


ECDHPublicKeyType = Union[ec.EllipticCurvePublicKey, x25519.X25519PublicKey]
ECDHPrivateKeyType = Union[ec.EllipticCurvePrivateKey, x25519.X25519PrivateKey]


def _encode_varint(value: int) -> bytes:
    """Encode an integer as a varint (Go-compatible)."""
    result = bytearray()
    while value > 127:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)


def _decode_varint(stream: io.BytesIO) -> int:
    """Decode a varint from a stream (Go-compatible)."""
    result = 0
    shift = 0
    while True:
        byte = stream.read(1)
        if not byte:
            raise DecryptionError("Unexpected end of data while reading varint")
        b = byte[0]
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
        if shift > 63:
            raise DecryptionError("Varint too large")
    return result


def _get_ecdh_key_for_public(public_key: ECDHPublicKeyType) -> ECDHPrivateKeyType:
    """Generate an ephemeral private key matching the public key's curve."""
    match public_key:
        case ec.EllipticCurvePublicKey():
            curve = public_key.curve
            return ec.generate_private_key(curve)
        case x25519.X25519PublicKey():
            return x25519.X25519PrivateKey.generate()
        case _:
            raise UnsupportedKeyTypeError(f"Unsupported public key type: {type(public_key).__name__}")


def _perform_ecdh(private_key: ECDHPrivateKeyType, public_key: ECDHPublicKeyType) -> bytes:
    """Perform ECDH key exchange."""
    match private_key:
        case ec.EllipticCurvePrivateKey():
            return private_key.exchange(ec.ECDH(), public_key)
        case x25519.X25519PrivateKey():
            return private_key.exchange(public_key)
        case _:
            raise UnsupportedKeyTypeError(f"Unsupported private key type: {type(private_key).__name__}")


def ecdh_encrypt(data: bytes, remote_public_key: ECDHPublicKeyType, rand: bytes | None = None) -> bytes:
    """
    Encrypt data for a recipient using ECDH.

    The format is:
    - version byte (0)
    - varint length of ephemeral public key
    - ephemeral public key (PKIX DER)
    - nonce (12 bytes for AES-GCM)
    - encrypted data with GCM tag

    Args:
        data: The data to encrypt
        remote_public_key: The recipient's public key
        rand: Optional random bytes for nonce (for testing); if None, uses os.urandom

    Returns:
        The encrypted data

    Raises:
        UnsupportedKeyTypeError: If the key type is not supported
    """
    # Generate ephemeral key pair matching the recipient's curve
    ephemeral_private = _get_ecdh_key_for_public(remote_public_key)
    ephemeral_public = ephemeral_private.public_key()

    # Perform ECDH
    shared_secret = _perform_ecdh(ephemeral_private, remote_public_key)

    # Derive AES key from shared secret
    secret_hash = bytearray(hash_data(shared_secret, hashlib.sha256))
    try:
        # Serialize ephemeral public key
        pub_bytes = marshal_pkix_public_key(ephemeral_public)

        # Create AES-GCM cipher
        aesgcm = AESGCM(bytes(secret_hash))

        # Generate nonce
        nonce = rand[:12] if rand else os.urandom(12)

        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, data, None)

        # Build output: version + pubkey_len + pubkey + nonce + ciphertext
        result = io.BytesIO()
        result.write(b'\x00')  # version 0
        result.write(_encode_varint(len(pub_bytes)))
        result.write(pub_bytes)
        result.write(nonce)
        result.write(ciphertext)

        return result.getvalue()
    finally:
        memclr(secret_hash)


def ecdh_decrypt(data: bytes, private_key: ECDHPrivateKeyType) -> bytes:
    """
    Decrypt data that was encrypted with ECDH.

    Args:
        data: The encrypted data
        private_key: The recipient's private key

    Returns:
        The decrypted data

    Raises:
        DecryptionError: If decryption fails
        UnsupportedKeyTypeError: If the key type is not supported
    """
    stream = io.BytesIO(data)

    # Read version
    version_byte = stream.read(1)
    if not version_byte:
        raise DecryptionError("Empty data")
    version = version_byte[0]

    if version != 0:
        raise DecryptionError(f"Unsupported message version {version}")

    # Read public key length
    pub_len = _decode_varint(stream)
    if pub_len > 65536:
        raise DecryptionError(f"Public key too large: {pub_len} bytes")

    # Read ephemeral public key
    pub_bytes = stream.read(pub_len)
    if len(pub_bytes) != pub_len:
        raise DecryptionError("Unexpected end of data while reading public key")

    try:
        ephemeral_public = parse_pkix_public_key(pub_bytes)
    except Exception as e:
        raise DecryptionError(f"Failed to parse ephemeral public key: {e}")

    # Verify key type compatibility
    if isinstance(private_key, ec.EllipticCurvePrivateKey):
        if not isinstance(ephemeral_public, ec.EllipticCurvePublicKey):
            raise DecryptionError("Key type mismatch: expected EC public key")
    elif isinstance(private_key, x25519.X25519PrivateKey):
        if not isinstance(ephemeral_public, x25519.X25519PublicKey):
            raise DecryptionError("Key type mismatch: expected X25519 public key")

    # Perform ECDH
    shared_secret = _perform_ecdh(private_key, ephemeral_public)

    # Derive AES key
    secret_hash = bytearray(hash_data(shared_secret, hashlib.sha256))
    try:
        # Create AES-GCM cipher
        aesgcm = AESGCM(bytes(secret_hash))

        # Read nonce (12 bytes for AES-GCM)
        nonce = stream.read(12)
        if len(nonce) != 12:
            raise DecryptionError("Unexpected end of data while reading nonce")

        # Read remaining ciphertext
        ciphertext = stream.read()
        if not ciphertext:
            raise DecryptionError("No ciphertext found")

        # Decrypt
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {e}")
    finally:
        memclr(secret_hash)
