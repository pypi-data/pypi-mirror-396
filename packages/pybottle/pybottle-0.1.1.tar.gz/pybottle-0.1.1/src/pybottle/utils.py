"""Utility functions for cryptbottle."""

import hashlib
from typing import Callable


def hash_data(data: bytes, *algorithms: Callable[[], "hashlib._Hash"]) -> bytes:
    """
    Hash data using one or more hash algorithms in sequence.

    If multiple algorithms are provided, each subsequent hash is applied
    to the result of the previous hash.

    Args:
        data: The data to hash
        *algorithms: Hash algorithm constructors (e.g., hashlib.sha256)

    Returns:
        The final hash digest
    """
    result = data
    for algo in algorithms:
        h = algo()
        h.update(result)
        result = h.digest()
    return result


def memclr(data: bytearray | memoryview) -> None:
    """
    Clear sensitive data from memory.

    This function overwrites the buffer with zeros to help prevent
    sensitive data from lingering in memory.

    Note: This provides limited security guarantees in Python due to
    the language's memory model, but follows the principle of defense
    in depth.

    Args:
        data: A mutable buffer to clear (bytearray or memoryview)
    """
    for i in range(len(data)):
        data[i] = 0
