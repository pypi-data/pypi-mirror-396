"""Opener - for opening bottles."""

import json
from dataclasses import dataclass, field
from typing import Any

import cbor2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .bottle import (
    Bottle,
    MessageFormat,
    MessageSignature,
    as_cbor_bottle,
    as_json_bottle,
)
from .errors import NoAppropriateKeyError, VerifyFailedError
from .keychain import Keychain
from .pkix import marshal_pkix_public_key, parse_pkix_public_key
from .sign import verify
from .short import decrypt_short_buffer
from .utils import memclr


@dataclass
class OpenResult:
    """Result of opening a bottle."""
    decryption_count: int = 0  # Number of decryption layers
    signatures: list[MessageSignature] = field(default_factory=list)  # Verified signatures
    bottles: list[Bottle] = field(default_factory=list)  # All bottles encountered

    def last(self) -> Bottle:
        """
        Get the innermost bottle.

        Returns:
            The innermost bottle (contains relevant metadata)

        Raises:
            ValueError: If no bottles were processed
        """
        if not self.bottles:
            raise ValueError("OpenResult has no bottles")
        return self.bottles[-1]

    def first(self) -> Bottle:
        """
        Get the outermost bottle.

        Returns:
            The outermost bottle (what was passed to open)

        Raises:
            ValueError: If no bottles were processed
        """
        if not self.bottles:
            raise ValueError("OpenResult has no bottles")
        return self.bottles[0]

    def signed_by(self, signer: Any) -> bool:
        """
        Check if the message was signed by the given key.

        Args:
            signer: A public key object, PKIX bytes, or an IDCard

        Returns:
            True if signed by the given key
        """
        # Check if it's an IDCard-like object
        if hasattr(signer, "get_keys"):
            keys = signer.get_keys("sign")
            for key in keys:
                if self.signed_by(key):
                    return True
            return False

        # Convert to bytes if needed
        if isinstance(signer, bytes):
            signer_bytes = signer
        else:
            try:
                signer_bytes = marshal_pkix_public_key(signer)
            except Exception:
                return False

        # Check signatures
        for sig in self.signatures:
            if sig.signer == signer_bytes:
                return True
        return False


class Opener:
    """
    Opens bottles by decrypting and verifying signatures.

    An opener can be created with one or more private keys that
    will be used to attempt decryption.
    """

    def __init__(self, keychain: Keychain | None = None):
        """
        Create an opener.

        Args:
            keychain: A keychain containing private keys for decryption
        """
        self._keychain = keychain

    def open(self, bottle: Bottle) -> tuple[bytes, OpenResult]:
        """
        Open a bottle, decrypting and verifying signatures.

        Args:
            bottle: The bottle to open

        Returns:
            Tuple of (message bytes, OpenResult)

        Raises:
            NoAppropriateKeyError: If decryption is needed but no key available
            VerifyFailedError: If signature verification fails
        """
        result = OpenResult()
        current = bottle

        while True:
            result.bottles.append(current)

            # Verify all signatures
            for sig in current.signatures:
                public_key = parse_pkix_public_key(sig.signer)
                verify(public_key, current.message, sig.data)
                result.signatures.append(sig)

            match current.format:
                case MessageFormat.CLEAR_TEXT:
                    return current.message, result

                case MessageFormat.CBOR_BOTTLE:
                    current = Bottle.from_cbor(current.message)

                case MessageFormat.JSON_BOTTLE:
                    current = Bottle.from_json(current.message)

                case MessageFormat.AES:
                    if self._keychain is None:
                        raise NoAppropriateKeyError("No keychain available for decryption")

                    # Try to decrypt with available keys
                    key: bytes | None = None
                    last_error = NoAppropriateKeyError("No appropriate key available")

                    for recipient in current.recipients:
                        try:
                            priv_key = self._keychain.get_key(recipient.recipient)
                            key = decrypt_short_buffer(recipient.data, priv_key)
                            break
                        except Exception as e:
                            last_error = e
                            continue

                    if key is None:
                        raise last_error

                    # Decrypt the message
                    key_array = bytearray(key)
                    try:
                        aesgcm = AESGCM(bytes(key_array))
                        nonce = current.message[:12]
                        ciphertext = current.message[12:]
                        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
                    finally:
                        memclr(key_array)

                    result.decryption_count += 1
                    current = Bottle.from_cbor(decrypted)

    def open_cbor(self, data: bytes) -> tuple[bytes, OpenResult]:
        """
        Open a CBOR-encoded bottle.

        Args:
            data: CBOR-encoded bottle bytes

        Returns:
            Tuple of (message bytes, OpenResult)
        """
        return self.open(as_cbor_bottle(data))

    def open_json(self, data: bytes) -> tuple[bytes, OpenResult]:
        """
        Open a JSON-encoded bottle.

        Args:
            data: JSON-encoded bottle bytes

        Returns:
            Tuple of (message bytes, OpenResult)
        """
        return self.open(as_json_bottle(data))

    def unmarshal(self, bottle: Bottle, target_type: type | None = None) -> tuple[Any, OpenResult]:
        """
        Open a bottle and unmarshal its contents.

        Args:
            bottle: The bottle to open
            target_type: Optional type hint (not used, for future compatibility)

        Returns:
            Tuple of (unmarshaled data, OpenResult)
        """
        data, result = self.open(bottle)
        last_bottle = result.last()

        # Determine content type
        ct = last_bottle.header.get("ct", "cbor")

        if ct == "cbor":
            return cbor2.loads(data), result
        elif ct == "json":
            return json.loads(data), result
        else:
            raise ValueError(f"Unsupported content type: {ct}")

    def unmarshal_cbor(self, data: bytes, target_type: type | None = None) -> tuple[Any, OpenResult]:
        """Open a CBOR-encoded bottle and unmarshal contents."""
        return self.unmarshal(as_cbor_bottle(data), target_type)

    def unmarshal_json(self, data: bytes, target_type: type | None = None) -> tuple[Any, OpenResult]:
        """Open a JSON-encoded bottle and unmarshal contents."""
        return self.unmarshal(as_json_bottle(data), target_type)


def new_opener(*keys) -> Opener:
    """
    Create an opener with the given keys.

    Args:
        *keys: Private keys to add to the opener's keychain

    Returns:
        A new Opener instance
    """
    keychain = Keychain()
    for key in keys:
        keychain.add_key(key)
    return Opener(keychain)


# Empty opener for signature verification only
EMPTY_OPENER = Opener(None)
