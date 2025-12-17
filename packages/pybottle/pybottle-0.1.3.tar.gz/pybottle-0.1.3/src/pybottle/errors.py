"""Custom exceptions for cryptbottle."""


class CryptBottleError(Exception):
    """Base exception for all cryptbottle errors."""
    pass


class NoAppropriateKeyError(CryptBottleError):
    """No appropriate key available to open bottle."""
    pass


class VerifyFailedError(CryptBottleError):
    """Signature verification failed."""
    pass


class KeyNotFoundError(CryptBottleError):
    """The key was not found."""
    pass


class GroupNotFoundError(CryptBottleError):
    """The group was not found."""
    pass


class KeyUnfitError(CryptBottleError):
    """The provided key was not fit for the requested purpose."""
    pass


class EncryptNoRecipientError(CryptBottleError):
    """Cannot encrypt a message without at least one valid recipient."""
    pass


class UnsupportedKeyTypeError(CryptBottleError):
    """Unsupported key type."""
    pass


class DecryptionError(CryptBottleError):
    """Error during decryption."""
    pass


class InvalidBottleError(CryptBottleError):
    """Invalid bottle format or structure."""
    pass
