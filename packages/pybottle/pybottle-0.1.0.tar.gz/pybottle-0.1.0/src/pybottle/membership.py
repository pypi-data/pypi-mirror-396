"""Membership - group membership for IDCards."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import cbor2

from .errors import VerifyFailedError
from .pkix import marshal_pkix_public_key, parse_pkix_public_key
from .sign import sign, verify, SigningKeyType

if TYPE_CHECKING:
    from .idcard import IDCard


@dataclass
class Membership:
    """
    A membership in a group.

    Memberships link a subject (IDCard owner) to a group and are
    signed by the group's key.
    """
    subject: bytes | None  # Subject's public key (PKIX DER), None when stored in IDCard
    key: bytes  # Group key (PKIX DER)
    status: str  # Status: "valid", "suspended"
    issued: datetime  # Update time
    info: dict[str, str] = field(default_factory=dict)  # Subject information
    sign_key: bytes = b""  # Signing key (PKIX DER)
    signature: bytes = b""  # Signature

    def signature_bytes(self) -> bytes:
        """
        Get the bytes to sign/verify.

        Returns:
            CBOR-encoded membership data (without signature)
        """
        # Create canonical CBOR representation
        data = {
            1: self.subject,
            2: self.key,
            3: self.status,
            4: self.issued,
            5: self.info,
            6: self.sign_key,
            7: None,  # signature is None for signing
        }
        # Use canonical encoding
        return cbor2.dumps(data, canonical=True)

    def sign_membership(self, private_key: SigningKeyType) -> None:
        """
        Sign the membership.

        Args:
            private_key: The key to sign with

        Raises:
            ValueError: If subject is not set
        """
        if self.subject is None:
            raise ValueError("Subject must be set before signing")

        pub_bytes = marshal_pkix_public_key(private_key.public_key())
        self.sign_key = pub_bytes

        sig_bytes = self.signature_bytes()
        self.signature = sign(private_key, sig_bytes)

    def verify(self, group_id: "IDCard | None" = None) -> None:
        """
        Verify the membership signature.

        Args:
            group_id: Optional IDCard for the group to verify against

        Raises:
            VerifyFailedError: If verification fails
            ValueError: If subject is not set or signing key is invalid
        """
        if self.subject is None:
            raise ValueError("Subject must be set before verification")

        # Parse the signing key
        public_key = parse_pkix_public_key(self.sign_key)

        if group_id is None:
            # Verify signing key matches group key
            if self.sign_key != self.key:
                raise ValueError("Invalid signing key - must match group key when no IDCard provided")
        else:
            # Verify group ID matches
            if self.key != group_id.self_key:
                raise ValueError("Invalid group ID for verification")
            # Verify the signing key is authorized for signing
            group_id.test_key_purpose(public_key, "sign")

        # Verify the signature
        sig_bytes = self.signature_bytes()
        verify(public_key, sig_bytes, self.signature)

    def to_cbor_dict(self) -> dict:
        """Convert to CBOR dict format with integer keys."""
        return {
            1: self.subject,
            2: self.key,
            3: self.status,
            4: self.issued,
            5: self.info,
            6: self.sign_key,
            7: self.signature,
        }

    @classmethod
    def from_cbor_dict(cls, d: dict) -> "Membership":
        """Create from CBOR dict with integer keys."""
        return cls(
            subject=d.get(1),
            key=d[2],
            status=d[3],
            issued=d[4] if isinstance(d[4], datetime) else datetime.fromisoformat(d[4]),
            info=d.get(5, {}),
            sign_key=d.get(6, b""),
            signature=d.get(7, b""),
        )

    def to_cbor(self) -> bytes:
        """Serialize to CBOR bytes."""
        return cbor2.dumps(self.to_cbor_dict())

    @classmethod
    def from_cbor(cls, data: bytes) -> "Membership":
        """Deserialize from CBOR bytes."""
        d = cbor2.loads(data)
        return cls.from_cbor_dict(d)


def new_membership(member_idcard: "IDCard", group_key: bytes) -> Membership:
    """
    Create a new membership.

    Args:
        member_idcard: The member's IDCard
        group_key: The group's key (PKIX bytes)

    Returns:
        A new Membership
    """
    return Membership(
        subject=member_idcard.self_key,
        key=group_key,
        status="valid",
        issued=datetime.now(timezone.utc),
        info={},
        sign_key=b"",
        signature=b"",
    )
