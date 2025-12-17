"""Keychain for storing and managing private keys."""

from typing import Iterator, Any

from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, x25519

from .errors import KeyNotFoundError, UnsupportedKeyTypeError
from .pkix import encode_public_key, PrivateKeyType, PublicKeyType
from .sign import sign, SigningKeyType


class Keychain:
    """
    A keychain for storing private keys.

    Keys are indexed by their PKIX-encoded public key bytes.
    """

    def __init__(self):
        """Create an empty keychain."""
        self._keys: dict[bytes, PrivateKeyType] = {}
        self._sign_key: SigningKeyType | None = None

    def add_key(self, key: PrivateKeyType | "Keychain") -> None:
        """
        Add a private key to the keychain.

        If another Keychain is passed, all its keys will be added.

        Args:
            key: A private key or another Keychain

        Raises:
            UnsupportedKeyTypeError: If the key type is not supported
        """
        if isinstance(key, Keychain):
            # Add keys from another keychain
            for pub_bytes, priv_key in key._keys.items():
                self._keys[pub_bytes] = priv_key
            if self._sign_key is None and key._sign_key is not None:
                self._sign_key = key._sign_key
            return

        # Get the public key
        try:
            public_key = key.public_key()
        except AttributeError:
            raise UnsupportedKeyTypeError(f"Key of type {type(key).__name__} does not have a public_key() method")

        # Encode to PKIX
        pub_bytes = encode_public_key(public_key)
        self._keys[pub_bytes] = key

        # Set as signing key if applicable and none set yet
        if self._sign_key is None:
            if isinstance(key, (rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey, ed25519.Ed25519PrivateKey)):
                self._sign_key = key

    def add_keys(self, *keys: PrivateKeyType | "Keychain") -> None:
        """
        Add multiple keys to the keychain.

        Args:
            *keys: Private keys or Keychains to add
        """
        for key in keys:
            self.add_key(key)

    def get_key(self, public: bytes | PublicKeyType) -> PrivateKeyType:
        """
        Get the private key corresponding to a public key.

        Args:
            public: The public key (as PKIX bytes or a key object)

        Returns:
            The corresponding private key

        Raises:
            KeyNotFoundError: If no matching key is found
        """
        if isinstance(public, bytes):
            pub_bytes = public
        else:
            pub_bytes = encode_public_key(public)

        if pub_bytes in self._keys:
            return self._keys[pub_bytes]

        raise KeyNotFoundError("Key not found in keychain")

    def has_key(self, public: bytes | PublicKeyType) -> bool:
        """
        Check if a key exists in the keychain.

        Args:
            public: The public key (as PKIX bytes or a key object)

        Returns:
            True if the key exists
        """
        try:
            self.get_key(public)
            return True
        except KeyNotFoundError:
            return False

    def first_signer(self) -> SigningKeyType | None:
        """
        Get the first signing key that was added.

        Returns:
            The first signing key, or None if no signing keys exist
        """
        return self._sign_key

    def get_signer(self, public: bytes | PublicKeyType) -> SigningKeyType:
        """
        Get a signing key corresponding to a public key.

        Args:
            public: The public key (as PKIX bytes or a key object)

        Returns:
            The corresponding signing key

        Raises:
            KeyNotFoundError: If no matching key is found
            UnsupportedKeyTypeError: If the key cannot sign
        """
        key = self.get_key(public)
        if isinstance(key, (rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey, ed25519.Ed25519PrivateKey)):
            return key
        raise UnsupportedKeyTypeError(f"Key of type {type(key).__name__} cannot sign")

    def sign(self, public: bytes | PublicKeyType, data: bytes, **kwargs) -> bytes:
        """
        Sign data using a key from the keychain.

        Args:
            public: The public key identifying which private key to use
            data: The data to sign
            **kwargs: Additional arguments passed to sign()

        Returns:
            The signature

        Raises:
            KeyNotFoundError: If no matching key is found
        """
        signer = self.get_signer(public)
        return sign(signer, data, **kwargs)

    def all_keys(self) -> Iterator[PrivateKeyType]:
        """Iterate over all private keys in the keychain."""
        yield from self._keys.values()

    def all_signers(self) -> Iterator[SigningKeyType]:
        """Iterate over all signing-capable keys in the keychain."""
        for key in self._keys.values():
            if isinstance(key, (rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey, ed25519.Ed25519PrivateKey)):
                yield key

    def __len__(self) -> int:
        """Return the number of keys in the keychain."""
        return len(self._keys)

    def __contains__(self, public: bytes | PublicKeyType) -> bool:
        """Check if a key exists in the keychain."""
        return self.has_key(public)
