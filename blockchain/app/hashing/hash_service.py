"""Security event hashing service.

Generates SHA-256 hashes for canonicalized events and provides integrity verification.
"""

import hashlib
import hmac
from typing import Any, Dict

from app.hashing.canonicalizer import canonicalize_event


def generate_hash(event: Dict[str, Any]) -> str:
    """Generate a SHA-256 hexadecimal hash for a cybersecurity event.

    Args:
        event: Dictionary representing the cybersecurity event.

    Returns:
        str: 64-character lowercase SHA-256 hexadecimal string.
    """
    canonical_bytes = canonicalize_event(event)
    sha256_hash = hashlib.sha256(canonical_bytes).hexdigest().lower()
    return sha256_hash


def verify_hash(event: Dict[str, Any], expected_hash: str) -> bool:
    """Verify whether a cybersecurity event matches an expected SHA-256 hash.

    Args:
        event: Dictionary representing the cybersecurity event.
        expected_hash: The expected SHA-256 hash to verify against.

    Returns:
        bool: True if the computed hash matches expected_hash, False otherwise.
    """
    if not isinstance(expected_hash, str):
        return False

    current_hash = generate_hash(event)
    return hmac.compare_digest(current_hash, expected_hash.lower())
