"""Utility helper functions."""

import uuid
import re
from datetime import datetime
from typing import Optional


def generate_event_id() -> str:
    """Generate a unique event ID."""
    return f"EVT-{uuid.uuid4().hex[:8].upper()}"


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse various timestamp formats into datetime.
    
    Phase 2 will expand this with proper normalization.
    """
    # Simple ISO format for now
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def normalize_ip(ip: str) -> str:
    """Normalize IP address."""
    # Basic normalization
    return ip.strip()


def is_private_ip(ip: str) -> bool:
    """Check if IP is private (RFC 1918)."""
    private_networks = [
        r"^10\.", r"^172\.(1[6-9]|2[0-9]|3[0-1])\.", r"^192\.168\."
    ]
    return any(re.match(pattern, ip) for pattern in private_networks)