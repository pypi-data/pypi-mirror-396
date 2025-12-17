"""Tests for pybottle package."""

import pytest
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa, x25519

import pybottle
from pybottle import (
    Bottle,
    MessageFormat,
    new_bottle,
    marshal,
    Opener,
    new_opener,
    EMPTY_OPENER,
    IDCard,
    new_idcard,
    Keychain,
    sign,
    verify,
    marshal_pkix_public_key,
    parse_pkix_public_key,
    NoAppropriateKeyError,
    VerifyFailedError,
)


# ============================================================
# Key Generation Helpers
# ============================================================

def generate_ec_key():
    """Generate an ECDSA key pair using P-256."""
    return ec.generate_private_key(ec.SECP256R1())


def generate_ed25519_key():
    """Generate an Ed25519 key pair."""
    return ed25519.Ed25519PrivateKey.generate()


def generate_x25519_key():
    """Generate an X25519 key pair."""
    return x25519.X25519PrivateKey.generate()


def generate_rsa_key():
    """Generate an RSA key pair."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


# ============================================================
# PKIX Tests
# ============================================================

class TestPKIX:
    """Tests for PKIX key serialization."""

    def test_ec_key_round_trip(self):
        """Test EC key serialization and deserialization."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()

        # Marshal
        der = marshal_pkix_public_key(public_key)
        assert isinstance(der, bytes)
        assert len(der) > 0

        # Parse
        parsed = parse_pkix_public_key(der)
        assert isinstance(parsed, ec.EllipticCurvePublicKey)

        # Verify same key
        der2 = marshal_pkix_public_key(parsed)
        assert der == der2

    def test_ed25519_key_round_trip(self):
        """Test Ed25519 key serialization and deserialization."""
        private_key = generate_ed25519_key()
        public_key = private_key.public_key()

        der = marshal_pkix_public_key(public_key)
        parsed = parse_pkix_public_key(der)
        assert isinstance(parsed, ed25519.Ed25519PublicKey)

        der2 = marshal_pkix_public_key(parsed)
        assert der == der2

    def test_x25519_key_round_trip(self):
        """Test X25519 key serialization and deserialization."""
        private_key = generate_x25519_key()
        public_key = private_key.public_key()

        der = marshal_pkix_public_key(public_key)
        parsed = parse_pkix_public_key(der)
        assert isinstance(parsed, x25519.X25519PublicKey)

        der2 = marshal_pkix_public_key(parsed)
        assert der == der2


# ============================================================
# Signing Tests
# ============================================================

class TestSigning:
    """Tests for signing and verification."""

    def test_ec_sign_verify(self):
        """Test EC signing and verification."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()
        data = b"Hello, World!"

        signature = sign(private_key, data)
        assert isinstance(signature, bytes)

        # Should not raise
        verify(public_key, data, signature)

    def test_ed25519_sign_verify(self):
        """Test Ed25519 signing and verification."""
        private_key = generate_ed25519_key()
        public_key = private_key.public_key()
        data = b"Hello, World!"

        signature = sign(private_key, data)
        verify(public_key, data, signature)

    def test_rsa_sign_verify(self):
        """Test RSA signing and verification."""
        private_key = generate_rsa_key()
        public_key = private_key.public_key()
        data = b"Hello, World!"

        signature = sign(private_key, data)
        verify(public_key, data, signature)

    def test_verify_wrong_signature(self):
        """Test that wrong signature fails verification."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()
        data = b"Hello, World!"

        signature = sign(private_key, data)

        # Modify signature
        bad_sig = bytearray(signature)
        bad_sig[0] ^= 0xFF
        bad_sig = bytes(bad_sig)

        with pytest.raises(VerifyFailedError):
            verify(public_key, data, bad_sig)


# ============================================================
# Bottle Tests
# ============================================================

class TestBottle:
    """Tests for Bottle class."""

    def test_new_bottle(self):
        """Test creating a new bottle."""
        data = b"Hello, World!"
        bottle = new_bottle(data)

        assert bottle.message == data
        assert bottle.format == MessageFormat.CLEAR_TEXT
        assert len(bottle.recipients) == 0
        assert len(bottle.signatures) == 0

    def test_bottle_cbor_round_trip(self):
        """Test CBOR serialization round trip."""
        bottle = new_bottle(b"Test message")
        bottle.header["test"] = "value"

        cbor_data = bottle.to_cbor()
        parsed = Bottle.from_cbor(cbor_data)

        assert parsed.message == bottle.message
        assert parsed.header == bottle.header
        assert parsed.format == bottle.format

    def test_bottle_json_round_trip(self):
        """Test JSON serialization round trip."""
        bottle = new_bottle(b"Test message")
        bottle.header["test"] = "value"

        json_data = bottle.to_json()
        parsed = Bottle.from_json(json_data)

        assert parsed.message == bottle.message
        assert parsed.header == bottle.header

    def test_bottle_up(self):
        """Test nesting bottles."""
        bottle = new_bottle(b"Inner message")
        bottle.header["inner"] = True

        bottle.bottle_up()

        assert bottle.format == MessageFormat.CBOR_BOTTLE
        assert bottle.header == {}

        # Get child
        child = bottle.child()
        assert child.message == b"Inner message"
        assert child.header["inner"] == True

    def test_sign_bottle(self):
        """Test signing a bottle."""
        private_key = generate_ec_key()
        bottle = new_bottle(b"Sign me!")

        bottle.sign(private_key)

        assert len(bottle.signatures) == 1
        assert bottle.signatures[0].signer == marshal_pkix_public_key(private_key.public_key())

    def test_encrypt_bottle_ec(self):
        """Test encrypting a bottle with EC key."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()

        bottle = new_bottle(b"Secret message")
        bottle.encrypt(public_key)

        assert bottle.format == MessageFormat.AES
        assert len(bottle.recipients) == 1

    def test_encrypt_bottle_x25519(self):
        """Test encrypting a bottle with X25519 key."""
        private_key = generate_x25519_key()
        public_key = private_key.public_key()

        bottle = new_bottle(b"Secret message")
        bottle.encrypt(public_key)

        assert bottle.format == MessageFormat.AES
        assert len(bottle.recipients) == 1


# ============================================================
# Opener Tests
# ============================================================

class TestOpener:
    """Tests for Opener class."""

    def test_open_cleartext(self):
        """Test opening a cleartext bottle."""
        bottle = new_bottle(b"Hello, World!")

        data, result = EMPTY_OPENER.open(bottle)

        assert data == b"Hello, World!"
        assert result.decryption_count == 0
        assert len(result.signatures) == 0

    def test_open_signed(self):
        """Test opening a signed bottle."""
        private_key = generate_ec_key()
        bottle = new_bottle(b"Signed message")
        bottle.sign(private_key)

        data, result = EMPTY_OPENER.open(bottle)

        assert data == b"Signed message"
        assert len(result.signatures) == 1
        assert result.signed_by(private_key.public_key())

    def test_open_encrypted_ec(self):
        """Test opening an encrypted bottle with EC key."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()

        bottle = new_bottle(b"Secret message")
        bottle.encrypt(public_key)

        opener = new_opener(private_key)
        data, result = opener.open(bottle)

        assert data == b"Secret message"
        assert result.decryption_count == 1

    def test_open_encrypted_x25519(self):
        """Test opening an encrypted bottle with X25519 key."""
        private_key = generate_x25519_key()
        public_key = private_key.public_key()

        bottle = new_bottle(b"Secret message")
        bottle.encrypt(public_key)

        opener = new_opener(private_key)
        data, result = opener.open(bottle)

        assert data == b"Secret message"
        assert result.decryption_count == 1

    def test_open_encrypted_without_key(self):
        """Test that opening encrypted bottle without key fails."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()

        bottle = new_bottle(b"Secret message")
        bottle.encrypt(public_key)

        with pytest.raises(NoAppropriateKeyError):
            EMPTY_OPENER.open(bottle)

    def test_open_signed_and_encrypted(self):
        """Test opening a signed and encrypted bottle."""
        sender_key = generate_ec_key()
        recipient_key = generate_ec_key()

        # Create, encrypt, bottle up, and sign
        bottle = new_bottle(b"Signed and encrypted")
        bottle.encrypt(recipient_key.public_key())
        bottle.bottle_up()
        bottle.sign(sender_key)

        opener = new_opener(recipient_key)
        data, result = opener.open(bottle)

        assert data == b"Signed and encrypted"
        assert result.decryption_count == 1
        assert result.signed_by(sender_key.public_key())


# ============================================================
# Alice and Bob Scenario (matches Go test)
# ============================================================

class TestAliceAndBob:
    """Test the Alice and Bob scenario from Go tests."""

    def test_alice_to_bob(self):
        """Test Alice sending an encrypted message to Bob."""
        # Generate keys
        alice = generate_ec_key()
        bob = generate_ec_key()

        # Alice creates and encrypts a message for Bob
        bottle = new_bottle(b"s.o.s. to the world")
        bottle.encrypt(bob.public_key())
        bottle.bottle_up()
        bottle.sign(alice)

        # Serialize
        cbor_data = bottle.to_cbor()

        # Bob opens the bottle
        opener = new_opener(bob)
        data, result = opener.open_cbor(cbor_data)

        assert data == b"s.o.s. to the world"
        assert result.signed_by(alice.public_key())
        assert result.decryption_count == 1

    def test_multiple_recipients(self):
        """Test encrypting for multiple recipients."""
        alice = generate_ec_key()
        bob = generate_ec_key()
        charlie = generate_ec_key()

        # Alice encrypts for Bob and Charlie
        bottle = new_bottle(b"Message for both")
        bottle.encrypt(bob.public_key(), charlie.public_key())

        # Bob can open it
        bob_opener = new_opener(bob)
        data, _ = bob_opener.open(bottle)
        assert data == b"Message for both"

        # Charlie can open it too
        charlie_opener = new_opener(charlie)
        data, _ = charlie_opener.open(bottle)
        assert data == b"Message for both"


# ============================================================
# IDCard Tests
# ============================================================

class TestIDCard:
    """Tests for IDCard class."""

    def test_new_idcard(self):
        """Test creating a new IDCard."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()

        idcard = new_idcard(public_key)

        assert idcard.self_key == marshal_pkix_public_key(public_key)
        assert len(idcard.sub_keys) == 1
        assert idcard.sub_keys[0].has_purpose("sign")

    def test_idcard_get_keys(self):
        """Test getting keys by purpose."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()

        idcard = new_idcard(public_key)

        sign_keys = idcard.get_keys("sign")
        assert len(sign_keys) == 1

        decrypt_keys = idcard.get_keys("decrypt")
        assert len(decrypt_keys) == 0

    def test_idcard_add_encryption_key(self):
        """Test adding an encryption key."""
        sign_key = generate_ec_key()
        encrypt_key = generate_x25519_key()

        idcard = new_idcard(sign_key.public_key())
        idcard.add_key_purpose(encrypt_key.public_key(), "decrypt")

        decrypt_keys = idcard.get_keys("decrypt")
        assert len(decrypt_keys) == 1

    def test_idcard_sign_and_unmarshal(self):
        """Test signing and unmarshaling an IDCard."""
        private_key = generate_ec_key()
        public_key = private_key.public_key()

        idcard = new_idcard(public_key)
        idcard.meta["name"] = "Test User"

        signed = idcard.sign(private_key)

        # Unmarshal
        parsed = IDCard.unmarshal(signed)

        assert parsed.self_key == idcard.self_key
        assert parsed.meta["name"] == "Test User"


# ============================================================
# Keychain Tests
# ============================================================

class TestKeychain:
    """Tests for Keychain class."""

    def test_add_and_get_key(self):
        """Test adding and retrieving keys."""
        keychain = Keychain()
        private_key = generate_ec_key()

        keychain.add_key(private_key)

        retrieved = keychain.get_key(private_key.public_key())
        assert retrieved == private_key

    def test_add_multiple_keys(self):
        """Test adding multiple keys."""
        keychain = Keychain()
        ec_key = generate_ec_key()
        ed_key = generate_ed25519_key()

        keychain.add_keys(ec_key, ed_key)

        assert len(keychain) == 2
        assert keychain.has_key(ec_key.public_key())
        assert keychain.has_key(ed_key.public_key())

    def test_first_signer(self):
        """Test getting the first signer."""
        keychain = Keychain()
        ec_key = generate_ec_key()
        x_key = generate_x25519_key()

        keychain.add_keys(x_key, ec_key)

        # First signing key should be ec_key (x25519 can't sign)
        assert keychain.first_signer() == ec_key


# ============================================================
# Marshal/Unmarshal Tests
# ============================================================

class TestMarshal:
    """Tests for marshal functions."""

    def test_marshal_dict(self):
        """Test marshaling a dictionary."""
        data = {"hello": "world", "count": 42}
        bottle = marshal(data)

        assert bottle.header["ct"] == "cbor"

        # Open and unmarshal
        result, _ = EMPTY_OPENER.unmarshal(bottle)
        assert result == data


# ============================================================
# Static Key Tests (for Go interoperability)
# ============================================================

class TestStaticKeys:
    """Tests using static keys matching Go cryptutil test keys."""

    def test_load_alice_bob(self):
        """Test loading Alice and Bob's ECDSA keys."""
        from pybottle.testkeys import get_alice, get_bob

        alice = get_alice()
        bob = get_bob()

        assert isinstance(alice, ec.EllipticCurvePrivateKey)
        assert isinstance(bob, ec.EllipticCurvePrivateKey)

        # Verify they're different keys
        alice_pub = marshal_pkix_public_key(alice.public_key())
        bob_pub = marshal_pkix_public_key(bob.public_key())
        assert alice_pub != bob_pub

    def test_load_chloe_daniel(self):
        """Test loading Chloe and Daniel's Ed25519 keys."""
        from pybottle.testkeys import get_chloe, get_daniel

        chloe = get_chloe()
        daniel = get_daniel()

        assert isinstance(chloe, ed25519.Ed25519PrivateKey)
        assert isinstance(daniel, ed25519.Ed25519PrivateKey)

    def test_static_alice_to_bob(self):
        """Test Alice sending to Bob with static keys."""
        from pybottle.testkeys import get_alice, get_bob

        alice = get_alice()
        bob = get_bob()

        # Alice sends encrypted message to Bob
        bottle = new_bottle(b"Hello Bob from Alice!")
        bottle.encrypt(bob.public_key())
        bottle.bottle_up()
        bottle.sign(alice)

        cbor_data = bottle.to_cbor()

        # Bob opens
        opener = new_opener(bob)
        data, result = opener.open_cbor(cbor_data)

        assert data == b"Hello Bob from Alice!"
        assert result.signed_by(alice.public_key())

    def test_static_chloe_to_daniel_ed25519(self):
        """Test Chloe sending to Daniel with Ed25519 keys."""
        from pybottle.testkeys import get_chloe, get_daniel

        chloe = get_chloe()
        daniel = get_daniel()

        # Chloe signs a message
        bottle = new_bottle(b"Hello Daniel from Chloe!")
        bottle.sign(chloe)

        cbor_data = bottle.to_cbor()

        # Daniel verifies
        data, result = EMPTY_OPENER.open_cbor(cbor_data)

        assert data == b"Hello Daniel from Chloe!"
        assert result.signed_by(chloe.public_key())

    def test_mixed_keys_alice_to_chloe(self):
        """Test ECDSA Alice encrypting for Ed25519 Chloe."""
        from pybottle.testkeys import get_alice, get_chloe

        alice = get_alice()
        chloe = get_chloe()

        # Alice encrypts for Chloe (Ed25519 -> X25519 conversion)
        bottle = new_bottle(b"Cross-algorithm message!")
        bottle.encrypt(chloe.public_key())
        bottle.bottle_up()
        bottle.sign(alice)

        cbor_data = bottle.to_cbor()

        # Chloe opens
        opener = new_opener(chloe)
        data, result = opener.open_cbor(cbor_data)

        assert data == b"Cross-algorithm message!"
        assert result.signed_by(alice.public_key())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
