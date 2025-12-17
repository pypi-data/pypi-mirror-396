"""IDCard - identity card for cryptographic keys."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import cbor2

from .bottle import Bottle, new_bottle
from .errors import KeyNotFoundError, KeyUnfitError, GroupNotFoundError
from .pkix import encode_public_key, parse_pkix_public_key, PublicKeyType, keys_equal
from .sign import SigningKeyType


def _parse_timestamp(value) -> datetime:
    """Parse a timestamp from various formats."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        # Unix timestamp
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError(f"Cannot parse timestamp from {type(value)}")


@dataclass
class SubKey:
    """A subkey in an IDCard."""
    key: bytes  # Public key as PKIX DER
    issued: datetime  # Issuance date
    expires: datetime | None = None  # Expiration date (optional)
    purposes: list[str] = field(default_factory=list)  # Purposes: "sign", "decrypt"

    def has_purpose(self, purpose: str) -> bool:
        """Check if the key has the given purpose."""
        return purpose in self.purposes

    def add_purpose(self, *purposes: str) -> None:
        """Add purposes to the key."""
        for p in purposes:
            if p not in self.purposes:
                self.purposes.append(p)
        self.purposes.sort()

    def is_expired(self) -> bool:
        """Check if the key has expired."""
        if self.expires is None:
            return False
        return datetime.now(timezone.utc) > self.expires

    def to_cbor_dict(self) -> dict:
        """Convert to CBOR dict format with integer keys."""
        # Use Unix timestamp (integer) for issued/expires to match Go
        result = {
            1: self.key,
            2: int(self.issued.timestamp()),
            4: self.purposes if self.purposes else None,
        }
        if self.expires is not None:
            result[3] = int(self.expires.timestamp())
        return result

    @classmethod
    def from_cbor_dict(cls, d: dict) -> "SubKey":
        """Create from CBOR dict with integer keys."""
        expires = d.get(3)
        return cls(
            key=d[1],
            issued=_parse_timestamp(d[2]),
            expires=_parse_timestamp(expires) if expires is not None else None,
            purposes=d.get(4, []),
        )

    def __repr__(self) -> str:
        import base64
        key_b64 = base64.urlsafe_b64encode(self.key).rstrip(b'=').decode('ascii')
        if self.expires:
            return f"SubKey[{key_b64} purposes:{self.purposes} issued:{self.issued} expires:{self.expires}]"
        return f"SubKey[{key_b64} purposes:{self.purposes} issued:{self.issued}]"


# Forward declaration for Membership type hint
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .membership import Membership


@dataclass
class IDCard:
    """
    An identity card for a cryptographic key.

    IDCards allow a signing key to specify additional keys for
    encryption/decryption and manage group memberships.
    """
    self_key: bytes  # Own public key (PKIX DER)
    issued: datetime  # Issuance date
    sub_keys: list[SubKey] = field(default_factory=list)  # Known subkeys
    revoke: list[SubKey] = field(default_factory=list)  # Revoked keys
    groups: list["Membership"] = field(default_factory=list)  # Group memberships
    meta: dict[str, str] = field(default_factory=dict)  # Metadata

    def get_keys(self, purpose: str) -> list[PublicKeyType]:
        """
        Get all keys that fit a given purpose.

        Args:
            purpose: The purpose to filter by (e.g., "sign", "decrypt")

        Returns:
            List of public key objects
        """
        result = []
        for sub in self.sub_keys:
            if not sub.has_purpose(purpose):
                continue
            if sub.is_expired():
                continue
            try:
                key = parse_pkix_public_key(sub.key)
                result.append(key)
            except Exception:
                pass
        return result

    def find_key(self, key: PublicKeyType | bytes, create: bool = False) -> SubKey:
        """
        Find a SubKey matching the given key.

        Args:
            key: The key to find (public key object or PKIX bytes)
            create: If True, create a new SubKey if not found

        Returns:
            The matching SubKey

        Raises:
            KeyNotFoundError: If not found and create=False
        """
        if not isinstance(key, bytes):
            key_bytes = encode_public_key(key)
        else:
            key_bytes = key

        for sub in self.sub_keys:
            if sub.key == key_bytes:
                return sub

        if not create:
            raise KeyNotFoundError("Key not found in IDCard")

        sub = SubKey(
            key=key_bytes,
            issued=datetime.now(timezone.utc),
            purposes=[],
        )
        self.sub_keys.append(sub)
        return sub

    def find_group(self, key: PublicKeyType | bytes) -> "Membership":
        """
        Find a group membership by group key.

        Args:
            key: The group key to find

        Returns:
            The matching Membership

        Raises:
            GroupNotFoundError: If not found
        """
        if not isinstance(key, bytes):
            key_bytes = encode_public_key(key)
        else:
            key_bytes = key

        for g in self.groups:
            if g.key == key_bytes:
                return g

        raise GroupNotFoundError("Group not found in IDCard")

    def test_key_purpose(self, key: PublicKeyType | bytes, purpose: str) -> None:
        """
        Test if a key is fit for a given purpose.

        Args:
            key: The key to test
            purpose: The required purpose

        Raises:
            KeyNotFoundError: If key not found
            KeyUnfitError: If key doesn't have the purpose
        """
        sub = self.find_key(key, create=False)
        if not sub.has_purpose(purpose):
            raise KeyUnfitError(f"Key not fit for purpose {purpose}")

    def set_key_purposes(self, key: PublicKeyType, *purposes: str) -> None:
        """
        Set the purposes for a key.

        Args:
            key: The key to modify
            *purposes: The purposes to set
        """
        sub = self.find_key(key, create=True)
        sub.purposes = sorted(list(purposes))

    def add_key_purpose(self, key: PublicKeyType, *purposes: str) -> None:
        """
        Add purposes to a key.

        Args:
            key: The key to modify
            *purposes: The purposes to add
        """
        sub = self.find_key(key, create=True)
        sub.add_purpose(*purposes)

    def set_key_expiration(self, key: PublicKeyType, expires: datetime) -> None:
        """
        Set the expiration for a key.

        Args:
            key: The key to modify
            expires: The expiration datetime
        """
        sub = self.find_key(key, create=True)
        sub.expires = expires

    def to_cbor_dict(self) -> dict:
        """Convert to CBOR dict format with integer keys."""
        # Use Unix timestamp (integer) for issued to match Go
        # Use None instead of [] or {} for empty collections to match Go's nil slices
        result = {
            1: self.self_key,
            2: int(self.issued.timestamp()),
            3: [s.to_cbor_dict() for s in self.sub_keys] if self.sub_keys else None,
            4: [r.to_cbor_dict() for r in self.revoke] if self.revoke else None,
            5: [g.to_cbor_dict() for g in self.groups] if self.groups else None,
            6: self.meta if self.meta else None,
        }
        return result

    @classmethod
    def from_cbor_dict(cls, d: dict) -> "IDCard":
        """Create from CBOR dict with integer keys."""
        from .membership import Membership

        return cls(
            self_key=d[1],
            issued=_parse_timestamp(d[2]),
            sub_keys=[SubKey.from_cbor_dict(s) for s in (d.get(3) or [])],
            revoke=[SubKey.from_cbor_dict(r) for r in (d.get(4) or [])],
            groups=[Membership.from_cbor_dict(g) for g in (d.get(5) or [])],
            meta=d.get(6) or {},
        )

    def to_cbor(self) -> bytes:
        """Serialize to CBOR bytes."""
        return cbor2.dumps(self.to_cbor_dict())

    @classmethod
    def from_cbor(cls, data: bytes) -> "IDCard":
        """Deserialize from CBOR bytes."""
        d = cbor2.loads(data)
        return cls.from_cbor_dict(d)

    def sign(self, private_key: SigningKeyType) -> bytes:
        """
        Sign the IDCard and return a signed bottle.

        Args:
            private_key: The key to sign with

        Returns:
            CBOR-encoded signed bottle
        """
        # Create bottle with IDCard content
        content = self.to_cbor()
        bottle = new_bottle(content)
        bottle.header["ct"] = "idcard"
        bottle.bottle_up()
        bottle.sign(private_key)

        return bottle.to_cbor()

    @classmethod
    def load(cls, data: bytes) -> "IDCard":
        """
        Load a signed IDCard from bytes.

        Args:
            data: CBOR-encoded signed bottle

        Returns:
            The IDCard

        Raises:
            ValueError: If not properly signed by the owner
        """
        from .opener import EMPTY_OPENER

        content, result = EMPTY_OPENER.open_cbor(data)
        idcard = cls.from_cbor(content)

        # Verify it's signed by the owner
        is_signed = False
        for sig in result.signatures:
            if sig.signer == idcard.self_key:
                is_signed = True
                break

        if not is_signed:
            raise ValueError("IDCard is not signed by the owner")

        return idcard


def new_idcard(public_key: PublicKeyType) -> IDCard:
    """
    Create a new IDCard for a public key.

    Args:
        public_key: The public key for this identity

    Returns:
        A new IDCard
    """
    pub_bytes = encode_public_key(public_key)
    now = datetime.now(timezone.utc)

    return IDCard(
        self_key=pub_bytes,
        issued=now,
        sub_keys=[
            SubKey(
                key=pub_bytes,
                issued=now,
                purposes=["sign"],
            )
        ],
        revoke=[],
        groups=[],
        meta={},
    )
