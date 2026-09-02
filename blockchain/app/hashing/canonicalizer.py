"""Canonicalizer module for cybersecurity events.

Provides deterministic JSON serialization to ensure consistent byte representation
prior to cryptographic hashing.
"""

import json
from typing import Any, Dict


def canonicalize_event(event: Dict[str, Any]) -> bytes:
    """Canonicalize a security event dictionary into deterministic UTF-8 encoded bytes.

    Args:
        event: Dictionary representing the cybersecurity event.

    Returns:
        bytes: Canonical UTF-8 byte sequence with sorted keys and compact separators.
    """
    if not isinstance(event, dict):
        raise TypeError(f"Expected event to be a dict, got {type(event).__name__}")

    # Deterministic JSON: sorted keys, compact separators, UTF-8 encoded
    canonical_json_str = json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return canonical_json_str.encode("utf-8")
