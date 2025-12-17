"""Bottle - a signed, encrypted message container."""

import json
import os
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Protocol

import cbor2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .errors import EncryptNoRecipientError, UnsupportedKeyTypeError
from .pkix import encode_public_key, PublicKeyType
from .sign import sign, SigningKeyType
from .short import encrypt_short_buffer
from .utils import memclr


class MessageFormat(IntEnum):
    """Format of the message content."""
    CLEAR_TEXT = 0   # Plain message
    CBOR_BOTTLE = 1  # CBOR-encoded nested bottle
    AES = 2          # AES-GCM encrypted (contains CBOR bottle)
    JSON_BOTTLE = 3  # JSON-encoded nested bottle


@dataclass
class MessageRecipient:
    """A recipient entry in an encrypted bottle."""
    type: int  # Always 0 for now
    recipient: bytes  # Recipient's public key (PKIX DER)
    data: bytes  # Encrypted key payload

    def to_cbor_array(self) -> list:
        """Convert to CBOR array format."""
        return [self.type, self.recipient, self.data]

    @classmethod
    def from_cbor_array(cls, arr: list) -> "MessageRecipient":
        """Create from CBOR array format."""
        return cls(type=arr[0], recipient=arr[1], data=arr[2])


@dataclass
class MessageSignature:
    """A signature entry in a signed bottle."""
    type: int  # Always 0 for now
    signer: bytes  # Signer's public key (PKIX DER)
    data: bytes  # Signature payload

    def to_cbor_array(self) -> list:
        """Convert to CBOR array format."""
        return [self.type, self.signer, self.data]

    @classmethod
    def from_cbor_array(cls, arr: list) -> "MessageSignature":
        """Create from CBOR array format."""
        return cls(type=arr[0], signer=arr[1], data=arr[2])


class KeyProvider(Protocol):
    """Protocol for objects that provide keys for a purpose."""
    def get_keys(self, purpose: str) -> list[PublicKeyType]:
        ...


@dataclass
class Bottle:
    """
    A signed, encrypted message container.

    Bottles can contain plain messages, other bottles (nested), or
    encrypted content. They can have multiple signatures and be
    encrypted for multiple recipients.
    """
    header: dict[str, Any] = field(default_factory=dict)
    message: bytes = b""
    format: MessageFormat = MessageFormat.CLEAR_TEXT
    recipients: list[MessageRecipient] = field(default_factory=list)
    signatures: list[MessageSignature] = field(default_factory=list)

    def to_cbor_array(self) -> list:
        """Convert to CBOR array format (matches Go's cbor:",toarray")."""
        return [
            self.header,
            self.message,
            int(self.format),
            [r.to_cbor_array() for r in self.recipients] if self.recipients else [],
            [s.to_cbor_array() for s in self.signatures] if self.signatures else [],
        ]

    @classmethod
    def from_cbor_array(cls, arr: list) -> "Bottle":
        """Create from CBOR array format."""
        return cls(
            header=arr[0] if arr[0] else {},
            message=arr[1],
            format=MessageFormat(arr[2]),
            recipients=[MessageRecipient.from_cbor_array(r) for r in arr[3]] if arr[3] else [],
            signatures=[MessageSignature.from_cbor_array(s) for s in arr[4]] if arr[4] else [],
        )

    def to_cbor(self) -> bytes:
        """Serialize to CBOR bytes."""
        return cbor2.dumps(self.to_cbor_array())

    @classmethod
    def from_cbor(cls, data: bytes) -> "Bottle":
        """Deserialize from CBOR bytes."""
        arr = cbor2.loads(data)
        return cls.from_cbor_array(arr)

    def to_json(self) -> bytes:
        """Serialize to JSON bytes."""
        import base64
        obj = {
            "hdr": self.header,
            "msg": base64.b64encode(self.message).decode('ascii'),
            "fmt": int(self.format),
            "dst": [
                {"typ": r.type, "key": base64.b64encode(r.recipient).decode('ascii'),
                 "dat": base64.b64encode(r.data).decode('ascii')}
                for r in self.recipients
            ] if self.recipients else None,
            "sig": [
                {"typ": s.type, "key": base64.b64encode(s.signer).decode('ascii'),
                 "dat": base64.b64encode(s.data).decode('ascii')}
                for s in self.signatures
            ] if self.signatures else None,
        }
        # Remove None values
        obj = {k: v for k, v in obj.items() if v is not None}
        return json.dumps(obj).encode('utf-8')

    @classmethod
    def from_json(cls, data: bytes) -> "Bottle":
        """Deserialize from JSON bytes."""
        import base64
        obj = json.loads(data)
        return cls(
            header=obj.get("hdr", {}),
            message=base64.b64decode(obj.get("msg", "")),
            format=MessageFormat(obj.get("fmt", 0)),
            recipients=[
                MessageRecipient(
                    type=r.get("typ", 0),
                    recipient=base64.b64decode(r["key"]),
                    data=base64.b64decode(r["dat"]),
                )
                for r in obj.get("dst", [])
            ] if obj.get("dst") else [],
            signatures=[
                MessageSignature(
                    type=s.get("typ", 0),
                    signer=base64.b64decode(s["key"]),
                    data=base64.b64decode(s["dat"]),
                )
                for s in obj.get("sig", [])
            ] if obj.get("sig") else [],
        )

    def is_clean_bottle(self) -> bool:
        """Check if this is a clean bottle (CBOR format, no signatures)."""
        return self.format == MessageFormat.CBOR_BOTTLE and len(self.signatures) == 0

    def bottle_up(self) -> None:
        """
        Encode the current bottle into itself.

        This creates a nested bottle, allowing additional layers
        of encryption or signatures to be applied.
        """
        encoded = self.to_cbor()
        self.header = {}
        self.message = encoded
        self.format = MessageFormat.CBOR_BOTTLE
        self.recipients = []
        self.signatures = []

    def child(self) -> "Bottle":
        """
        Get the child bottle (reverse of bottle_up).

        Returns:
            The nested bottle

        Raises:
            ValueError: If the bottle doesn't contain another bottle
        """
        if self.format == MessageFormat.CBOR_BOTTLE:
            return Bottle.from_cbor(self.message)
        elif self.format == MessageFormat.JSON_BOTTLE:
            return Bottle.from_json(self.message)
        else:
            raise ValueError("Bottle does not contain another bottle or it is encrypted")

    def encrypt(self, *recipients: PublicKeyType | KeyProvider) -> None:
        """
        Encrypt the bottle for the given recipients.

        Any recipient will be able to decrypt the bottle.

        Args:
            *recipients: Public keys or KeyProvider objects

        Raises:
            EncryptNoRecipientError: If no valid recipients
        """
        # Ensure we're dealing with a clean bottle
        if not self.is_clean_bottle():
            self.bottle_up()

        # Generate random AES key
        key = bytearray(os.urandom(32))
        try:
            # Create AES-GCM cipher
            aesgcm = AESGCM(bytes(key))

            # Generate nonce
            nonce = os.urandom(12)

            # Encrypt the message
            ciphertext = aesgcm.encrypt(nonce, self.message, None)

            # Build recipients list
            all_recipients: list[MessageRecipient] = []
            for recipient in recipients:
                recipient_entries = _make_recipients(bytes(key), recipient)
                all_recipients.extend(recipient_entries)

            if not all_recipients:
                raise EncryptNoRecipientError("Cannot encrypt without at least one valid recipient")

            # Update bottle
            self.message = nonce + ciphertext
            self.format = MessageFormat.AES
            self.recipients = all_recipients

        finally:
            memclr(key)

    def sign(self, private_key: SigningKeyType) -> None:
        """
        Sign the bottle.

        Multiple signatures can be added by calling this multiple times.
        If the header is not empty, the bottle will be bottled up first
        to ensure the header is included in the signature.

        Args:
            private_key: The key to sign with
        """
        # If header has content, bottle up first
        if self.header:
            self.bottle_up()

        # Get public key
        public_key = private_key.public_key()
        pub_bytes = encode_public_key(public_key)

        # Sign the message
        signature = sign(private_key, self.message)

        # Add signature
        self.signatures.append(MessageSignature(
            type=0,
            signer=pub_bytes,
            data=signature,
        ))


def new_bottle(data: bytes) -> Bottle:
    """
    Create a new bottle containing the given data.

    Args:
        data: The message data

    Returns:
        A new Bottle instance
    """
    return Bottle(
        header={},
        message=data,
        format=MessageFormat.CLEAR_TEXT,
        recipients=[],
        signatures=[],
    )


def wrap(data: Any) -> Bottle:
    """
    Create a bottle containing CBOR-encoded data.

    Args:
        data: The data to wrap

    Returns:
        A new Bottle with content-type set to "cbor"
    """
    encoded = cbor2.dumps(data)
    bottle = new_bottle(encoded)
    bottle.header["ct"] = "cbor"
    return bottle


def wrap_json(data: Any) -> Bottle:
    """
    Create a bottle containing JSON-encoded data.

    Args:
        data: The data to wrap

    Returns:
        A new Bottle with content-type set to "json"
    """
    encoded = json.dumps(data).encode('utf-8')
    bottle = new_bottle(encoded)
    bottle.header["ct"] = "json"
    return bottle


def as_cbor_bottle(data: bytes) -> Bottle:
    """
    Treat data as a CBOR-encoded bottle.

    Args:
        data: CBOR-encoded bottle bytes

    Returns:
        A Bottle container for the data
    """
    return Bottle(
        header={},
        message=data,
        format=MessageFormat.CBOR_BOTTLE,
        recipients=[],
        signatures=[],
    )


def as_json_bottle(data: bytes) -> Bottle:
    """
    Treat data as a JSON-encoded bottle.

    Args:
        data: JSON-encoded bottle bytes

    Returns:
        A Bottle container for the data
    """
    return Bottle(
        header={},
        message=data,
        format=MessageFormat.JSON_BOTTLE,
        recipients=[],
        signatures=[],
    )


def _make_recipients(key: bytes, recipient: PublicKeyType | KeyProvider) -> list[MessageRecipient]:
    """Create MessageRecipient entries for a recipient."""
    # Check if it's a KeyProvider (like IDCard)
    if hasattr(recipient, "get_keys"):
        keys = recipient.get_keys("decrypt")
        results = []
        for subkey in keys:
            results.extend(_make_recipients(key, subkey))
        return results

    # It's a public key
    try:
        encrypted = encrypt_short_buffer(key, recipient)
        pub_bytes = encode_public_key(recipient)
        return [MessageRecipient(type=0, recipient=pub_bytes, data=encrypted)]
    except UnsupportedKeyTypeError:
        return []
