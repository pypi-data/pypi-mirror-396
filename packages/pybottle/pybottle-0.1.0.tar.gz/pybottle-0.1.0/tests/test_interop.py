"""
Interoperability tests using pre-generated test data from Go cryptutil.

These tests verify that pybottle can correctly open bottles and IDCards
that were created by the Go implementation.
"""

import base64
import pytest

from pybottle import (
    IDCard,
    new_opener,
    EMPTY_OPENER,
    NoAppropriateKeyError,
)
from pybottle.testkeys import get_alice, get_bob, get_chloe, get_daniel


# Pre-generated test data from Go cryptutil (base64 standard encoding)
# Bottles
ALICE_SIGNED_CLEARTEXT = base64.b64decode(
    "haBRSGVsbG8gZnJvbSBBbGljZSEA9oGDAFhbMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE09oIghTDnluvtv0+NKMhTS2nfC3TzR4DWnZK7czzFPZSH6bJN5oMZCp5X7pfI4BbIyTVtGeRKg6GTpzzfE+KYFhHMEUCIQCPEWPr/SDCeJXS73kn0oQwXWH70EfgSPtlhyLhvRHHYQIgbvITapFSnsuY2dAQorY+mTLOsMYOJB95nucHxIOzUME="
)

CHLOE_SIGNED_CLEARTEXT = base64.b64decode(
    "haBRSGVsbG8gZnJvbSBDaGxvZSEA9oGDAFgsMCowBQYDK2VwAyEATL6PjuPHSTIG2UXmJfEMvJESSp7zLqTncBBc4ElE/D5YQPMG5xy/onBTIEHWfvlayb3lCTfGSClApscby4WP919SOs7c5iq7xsLrYkcGpwGCFKObAbT1C0+omag8EiDWNwY="
)

ALICE_TO_BOB_ENCRYPTED = base64.b64decode(
    "haBZAUSFoFhDm5+MnDHvHavDG26WIRahkvXRyopa5BCzFgv25By0k3ase9e/d7hvr+Eq7wKobH/11VQkZmc6gel8TtIAuutYZ7ZmqgKBgwBYWzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABIoEQn7veaBj/RTUi1qMYYQgxJoMWBvLTMJRSLcwLlelv38NDoNgTRt8nNKjm/nBCY0ClkSPYv5tRVHPe2o2k65YmQBbMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEu2rfO4Mdj5HJ+ahL7WVbBZXrSzD2FoOOAjqFQ7PDTSfIucQV0gWOjLjPLg7SQ5yiO3pv1RKzJLotq6UyKA3B6iMtBkT4Sn0fVU2Nw0fw0bBjZFj1MPCFnXGqK9Qd3/EyzTA5XzksY+EZaBkOej1ckTc1fpXTEn8HZuPa/PYB9oGDAFhbMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE09oIghTDnluvtv0+NKMhTS2nfC3TzR4DWnZK7czzFPZSH6bJN5oMZCp5X7pfI4BbIyTVtGeRKg6GTpzzfE+KYFhHMEUCIGgCMEL82ywkMC0PuAf4HUqS1wmnzXTtzUHSBy5Aok4ZAiEAn7pHkUVyWhCfb/aiGvwm0PW347iaKDOmywOwrZG1YNk="
)

CHLOE_TO_DANIEL_ENCRYPTED = base64.b64decode(
    "haBY6YWgWEbOz5dzuHVoDJGbbegel6QHqyxa7U7NuVznwNxeCQvqTgz8gEPb38MMsTxq5IR+Qu9cfgZ2a2/2DQg+0oJJPRl7ZUYrekXAAoGDAFgsMCowBQYDK2VwAyEA9lV/yry+XMvMGqwhUQXef+3FOjAGD4Mj/gxoJN3X+79YagAsMCowBQYDK2VuAyEAA943R8RqHeZffQ+TH4RlmrtXvklkBdKgddPyttXfvCxrZFHDb9X2oVfQRCbb4fIjc0VqVZT5HvVKf9bz+ymcWbkv+iWCc/Q+B8oLHebH9sE+0zytOy/e1Kamcir2AfaBgwBYLDAqMAUGAytlcAMhAEy+j47jx0kyBtlF5iXxDLyREkqe8y6k53AQXOBJRPw+WECeTEDNYixOSd2tj7BchCLVoLCkmr84L9CwxLo10mYgQoW5wZFOUEME0VdL3kaJfeHuX2/UiRWMk3rssnp6lJgO"
)

ALICE_TO_BOB_AND_DANIEL = base64.b64decode(
    "haBZAdmFoFg8uyjLChvFnHR+sq8bfbuziw/PeYrFriKzQSqZzQV3RWwGMsB1pz6hE9FnMqoIamLD2oM1HsHy1+GU8RERAoKDAFhbMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEigRCfu95oGP9FNSLWoxhhCDEmgxYG8tMwlFItzAuV6W/fw0Og2BNG3yc0qOb+cEJjQKWRI9i/m1FUc97ajaTrliZAFswWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAARF6feIhWN/vC1edEjEccG0ajlShDmBYyIrat0c+fz+yy43aIzQJKC5QQRpf8fG57Y5wZb3KhQIg63NOkYe3tIB1bsrUSWZUw/6uHoWAM1GT+oasplV4WxkRWzetoxH6vWtuRQgMzDTv9qjfSchaHpQgjMaPTknIqHNC8uRgwBYLDAqMAUGAytlcAMhAPZVf8q8vlzLzBqsIVEF3n/txTowBg+DI/4MaCTd1/u/WGoALDAqMAUGAytlbgMhAFuGnMFD6MCASWo8xOy9HSITAxPzu2UJuXSUCzRyZqYmy1uE1/Y7w1a3kOhitndcYPSMGnE7AKJmnjiAyf8vPnvv5ijUQlrm1Zcy+QavS33BopdG1HXKYxn6pF1r9gH2gYMAWFswWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATT2giCFMOeW6+2/T40oyFNLad8LdPNHgNadkrtzPMU9lIfpsk3mgxkKnlful8jgFsjJNW0Z5EqDoZOnPN8T4pgWEcwRQIge6OK+2IEUVmPo7ZSovRJ5IJb9dZTT2ZcGgp4A2erM80CIQC3HMt9VGk0+tpEyripSdfobx1TcRByY3CI6Gbr2sZjiA=="
)

ANONYMOUS_TO_BOB = base64.b64decode(
    "haBYOYK78ifrqu7W6Uh3vF7PnqUr8CNJ5cezriuZb+EzFZ/NdacKr6s37y5jRbnOw5seoUtp54ClCJjzWgKBgwBYWzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABIoEQn7veaBj/RTUi1qMYYQgxJoMWBvLTMJRSLcwLlelv38NDoNgTRt8nNKjm/nBCY0ClkSPYv5tRVHPe2o2k65YmQBbMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE4gO8JMnJc1wZLg7Ne1Ze3I4yKe7J7yRVnJTYe0PEkO8/61OFivv5YcdNZjNSoRvZx0O0KJEP7u1CtHDQPYcXbaGBQU/XVmP1NY0yepic+jWelsZNO8HScpaNY4HNtghcanOY0GDoZkokU5lvJzUARx1pmoowtqgSFkm6b/Y="
)

ALICE_AND_CHLOE_SIGNED = base64.b64decode(
    "haBYHlNpZ25lZCBieSBib3RoIEFsaWNlIGFuZCBDaGxvZQD2goMAWFswWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATT2giCFMOeW6+2/T40oyFNLad8LdPNHgNadkrtzPMU9lIfpsk3mgxkKnlful8jgFsjJNW0Z5EqDoZOnPN8T4pgWEYwRAIgKfCLaGT93SX/tGQvesD5y+XCNVLlcO9k2NJqVpA/IrYCIEnrnZ+9YdAGCjBvGt8IkPEJmrKpbDOlDx4zRr7WkYmngwBYLDAqMAUGAytlcAMhAEy+j47jx0kyBtlF5iXxDLyREkqe8y6k53AQXOBJRPw+WEBSiwkh3t4Q+Nrq/bRc6HNSjpJUo8GS22KgaJlUxAPnB8BfnOrp/zs07hJRgvtOrIy96BSRzDZSdDlNCpJ21zoE"
)

NESTED_BOB_THEN_DANIEL = base64.b64decode(
    "haBZAfyFoFkBWCYLkGEdT1Q7jJSGLAzAIZmXKmTQF9XDNNm9IGRxFJQaXYkhdyO4z67pw8Nrb6OZwRUNCvC12qYkW9iZdypuw8seyMwA7SAtXRsJTDpXF3WSauqwr7ayvurrzxSThFoQfWhJ71Eb2WrzwDmROYvl4Wm2ooAKzxYuutKjKuzVF5VeF0m3scOSjHlP7KSF3vo3GyAMLhVHBYeLx7MvrVxY98BxB09oED4GhlIKzq8BIcdHYmkn8ckhH8APwx/oHaBKI/m7ppBTUdqW9qIPAn/CJb7r6pZlvVx/oepDoH5291BJCj/YHTm/V+VCA9iGnw+3Oac+M4krD5/tiPph3yDsgGVg2SzF8S2FrhHd4b1tfqBMzecKcAhgFFHaZcP7hyVSVPry/QnkcSI85fKdgpQnyfoGGb1a9usdOMyQAW0G8ywIiI/IpU1Pm7rGQaQ3wlh25FYiC6ZfglvpAoGDAFgsMCowBQYDK2VwAyEA9lV/yry+XMvMGqwhUQXef+3FOjAGD4Mj/gxoJN3X+79YagAsMCowBQYDK2VuAyEAK7KqTeAgS1FkPMGF2jgEny1TmvsxRx3H70OLhhKy73oeSpRThl/5KQGRuuYDWDW4kyFrXjqJd7F0gzgSzOYD2QBIkKESzYHSPDr9xdGTnO43jC0tan2NKaFuCY32AfaBgwBYWzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABNPaCIIUw55br7b9PjSjIU0tp3wt080eA1p2Su3M8xT2Uh+myTeaDGQqeV+6XyOAWyMk1bRnkSoOhk6c83xPimBYRjBEAiAT7cGQNP43M/T+L3Ve1LBpMF2cb4WySB1g3qHXotcOdwIgDbXdEgVyXMM/j5rfIL+cIvck2SYfTdnA4zpYYctUNxA="
)

# IDCards
ALICE_IDCARD = base64.b64decode(
    "haBY/YWhYmN0ZmlkY2FyZFjspgFYWzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABNPaCIIUw55br7b9PjSjIU0tp3wt080eA1p2Su3M8xT2Uh+myTeaDGQqeV+6XyOAWyMk1bRnkSoOhk6c83xPimACGmk+hQMDgaMBWFswWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATT2giCFMOeW6+2/T40oyFNLad8LdPNHgNadkrtzPMU9lIfpsk3mgxkKnlful8jgFsjJNW0Z5EqDoZOnPN8T4pgAhppPoUDBIJnZGVjcnlwdGRzaWduBPYF9gahZG5hbWVlQWxpY2UA9vYB9oGDAFhbMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE09oIghTDnluvtv0+NKMhTS2nfC3TzR4DWnZK7czzFPZSH6bJN5oMZCp5X7pfI4BbIyTVtGeRKg6GTpzzfE+KYFhHMEUCIAM0VfD5ON6ajKxrR2sMcqlU+karsg4ha+HRWVJsPjWvAiEAlAx6nGF3vHDvV2wlzQ2qgwDuOXQ1dulxuZI+2UEL26Q="
)

BOB_IDCARD = base64.b64decode(
    "haBY+4WhYmN0ZmlkY2FyZFjqpgFYWzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABIoEQn7veaBj/RTUi1qMYYQgxJoMWBvLTMJRSLcwLlelv38NDoNgTRt8nNKjm/nBCY0ClkSPYv5tRVHPe2o2k64CGmk+hQMDgaMBWFswWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASKBEJ+73mgY/0U1ItajGGEIMSaDFgby0zCUUi3MC5Xpb9/DQ6DYE0bfJzSo5v5wQmNApZEj2L+bUVRz3tqNpOuAhppPoUDBIJnZGVjcnlwdGRzaWduBPYF9gahZG5hbWVjQm9iAPb2AfaBgwBYWzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABIoEQn7veaBj/RTUi1qMYYQgxJoMWBvLTMJRSLcwLlelv38NDoNgTRt8nNKjm/nBCY0ClkSPYv5tRVHPe2o2k65YRzBFAiEAufvr4HAcHDhwD7zrCXHfzqGbNCJKf2HzSVPMXEARoRYCIEZnD7EobO3zNmDSJLXf6mMi4WWqr9qLEwl3poV/x9wv"
)

CHLOE_IDCARD = base64.b64decode(
    "haBYn4WhYmN0ZmlkY2FyZFiOpgFYLDAqMAUGAytlcAMhAEy+j47jx0kyBtlF5iXxDLyREkqe8y6k53AQXOBJRPw+AhppPoUDA4GjAVgsMCowBQYDK2VwAyEATL6PjuPHSTIG2UXmJfEMvJESSp7zLqTncBBc4ElE/D4CGmk+hQMEgmdkZWNyeXB0ZHNpZ24E9gX2BqFkbmFtZWVDaGxvZQD29gH2gYMAWCwwKjAFBgMrZXADIQBMvo+O48dJMgbZReYl8Qy8kRJKnvMupOdwEFzgSUT8PlhAzjf6zY5rD2kD0/12qFbscTK6Ib6OsssCoZaIyNpDOKFGLMTiMGHS3k+Ha9bHGcBo/DuoSWuDrxj/WThyRx0YBA=="
)

DANIEL_IDCARD = base64.b64decode(
    "haBYoIWhYmN0ZmlkY2FyZFiPpgFYLDAqMAUGAytlcAMhAPZVf8q8vlzLzBqsIVEF3n/txTowBg+DI/4MaCTd1/u/AhppPoUDA4GjAVgsMCowBQYDK2VwAyEA9lV/yry+XMvMGqwhUQXef+3FOjAGD4Mj/gxoJN3X+78CGmk+hQMEgmdkZWNyeXB0ZHNpZ24E9gX2BqFkbmFtZWZEYW5pZWwA9vYB9oGDAFgsMCowBQYDK2VwAyEA9lV/yry+XMvMGqwhUQXef+3FOjAGD4Mj/gxoJN3X+79YQH4yeA5Oluwr9Av5EjDcMBo11ax2eNKVtDvLK37V4DCMr6rF4y41oRXiud9sr4Lwg0AGeW+OE9S14N5Emzj4GQQ="
)


class TestPregenBottles:
    """Tests for pre-generated bottles from Go cryptutil."""

    def test_alice_signed_cleartext(self):
        """Test opening Alice's signed cleartext message."""
        alice = get_alice()

        data, result = EMPTY_OPENER.open_cbor(ALICE_SIGNED_CLEARTEXT)

        assert data == b"Hello from Alice!"
        assert result.signed_by(alice.public_key())
        assert result.decryption_count == 0

    def test_chloe_signed_cleartext(self):
        """Test opening Chloe's signed cleartext message."""
        chloe = get_chloe()

        data, result = EMPTY_OPENER.open_cbor(CHLOE_SIGNED_CLEARTEXT)

        assert data == b"Hello from Chloe!"
        assert result.signed_by(chloe.public_key())
        assert result.decryption_count == 0

    def test_alice_to_bob_encrypted(self):
        """Test opening Alice's encrypted message to Bob."""
        alice = get_alice()
        bob = get_bob()

        opener = new_opener(bob)
        data, result = opener.open_cbor(ALICE_TO_BOB_ENCRYPTED)

        assert data == b"Secret message from Alice to Bob"
        assert result.signed_by(alice.public_key())
        assert result.decryption_count == 1

        # Should fail without Bob's key
        with pytest.raises(NoAppropriateKeyError):
            EMPTY_OPENER.open_cbor(ALICE_TO_BOB_ENCRYPTED)

    def test_chloe_to_daniel_encrypted(self):
        """Test opening Chloe's encrypted message to Daniel."""
        chloe = get_chloe()
        daniel = get_daniel()

        opener = new_opener(daniel)
        data, result = opener.open_cbor(CHLOE_TO_DANIEL_ENCRYPTED)

        assert data == b"Secret message from Chloe to Daniel"
        assert result.signed_by(chloe.public_key())
        assert result.decryption_count == 1

    def test_alice_to_bob_and_daniel(self):
        """Test opening Alice's message encrypted for both Bob and Daniel."""
        alice = get_alice()
        bob = get_bob()
        daniel = get_daniel()

        # Open with Bob's key
        opener_bob = new_opener(bob)
        data, result = opener_bob.open_cbor(ALICE_TO_BOB_AND_DANIEL)

        assert data == b"Secret for Bob and Daniel"
        assert result.signed_by(alice.public_key())

        # Open with Daniel's key
        opener_daniel = new_opener(daniel)
        data2, result2 = opener_daniel.open_cbor(ALICE_TO_BOB_AND_DANIEL)

        assert data2 == b"Secret for Bob and Daniel"
        assert result2.signed_by(alice.public_key())

    def test_anonymous_to_bob(self):
        """Test opening anonymous encrypted message to Bob."""
        bob = get_bob()

        opener = new_opener(bob)
        data, result = opener.open_cbor(ANONYMOUS_TO_BOB)

        assert data == b"Anonymous secret to Bob"
        assert len(result.signatures) == 0
        assert result.decryption_count == 1

    def test_alice_and_chloe_signed(self):
        """Test opening message signed by both Alice and Chloe."""
        alice = get_alice()
        chloe = get_chloe()

        data, result = EMPTY_OPENER.open_cbor(ALICE_AND_CHLOE_SIGNED)

        assert data == b"Signed by both Alice and Chloe"
        assert result.signed_by(alice.public_key())
        assert result.signed_by(chloe.public_key())
        assert len(result.signatures) == 2

    def test_nested_bob_then_daniel(self):
        """Test opening doubly encrypted message (Bob outer, Daniel inner)."""
        alice = get_alice()
        bob = get_bob()
        daniel = get_daniel()

        # Need both keys to decrypt nested bottle
        opener = new_opener(bob, daniel)
        data, result = opener.open_cbor(NESTED_BOB_THEN_DANIEL)

        assert data == b"Doubly encrypted message"
        assert result.signed_by(alice.public_key())
        assert result.decryption_count == 2

        # Should fail with only Daniel's key (outer layer needs Bob)
        opener_daniel_only = new_opener(daniel)
        with pytest.raises(Exception):  # Will fail at outer layer
            opener_daniel_only.open_cbor(NESTED_BOB_THEN_DANIEL)


class TestPregenIDCards:
    """Tests for pre-generated IDCards from Go cryptutil."""

    def test_alice_idcard(self):
        """Test unmarshaling Alice's IDCard."""
        alice = get_alice()

        idcard = IDCard.unmarshal(ALICE_IDCARD)

        assert idcard.meta["name"] == "Alice"
        # Check key purposes
        idcard.test_key_purpose(alice.public_key(), "sign")
        idcard.test_key_purpose(alice.public_key(), "decrypt")

    def test_bob_idcard(self):
        """Test unmarshaling Bob's IDCard."""
        bob = get_bob()

        idcard = IDCard.unmarshal(BOB_IDCARD)

        assert idcard.meta["name"] == "Bob"
        idcard.test_key_purpose(bob.public_key(), "sign")
        idcard.test_key_purpose(bob.public_key(), "decrypt")

    def test_chloe_idcard(self):
        """Test unmarshaling Chloe's IDCard."""
        chloe = get_chloe()

        idcard = IDCard.unmarshal(CHLOE_IDCARD)

        assert idcard.meta["name"] == "Chloe"
        idcard.test_key_purpose(chloe.public_key(), "sign")
        idcard.test_key_purpose(chloe.public_key(), "decrypt")

    def test_daniel_idcard(self):
        """Test unmarshaling Daniel's IDCard."""
        daniel = get_daniel()

        idcard = IDCard.unmarshal(DANIEL_IDCARD)

        assert idcard.meta["name"] == "Daniel"
        idcard.test_key_purpose(daniel.public_key(), "sign")
        idcard.test_key_purpose(daniel.public_key(), "decrypt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
