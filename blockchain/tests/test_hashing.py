"""Tests for cybersecurity event hashing and verification."""

import string

from app.hashing.hash_service import generate_hash, verify_hash


def test_hash_generation():
    """Test SHA-256 hash generation for a security event."""
    sample_event = {
        "alert_id": "ALT-2026-0091",
        "attack_type": "SQL_INJECTION",
        "risk_score": 85,
        "severity": "HIGH",
    }
    event_hash = generate_hash(sample_event)

    assert isinstance(event_hash, str)
    assert len(event_hash) == 64
    assert all(c in string.hexdigits for c in event_hash)
    assert event_hash == event_hash.lower()


def test_successful_verification():
    """Test successful integrity verification for an unchanged event."""
    sample_event = {
        "alert_id": "ALT-2026-0092",
        "attack_type": "DDOS_SYN_FLOOD",
        "risk_score": 92,
        "severity": "CRITICAL",
    }
    event_hash = generate_hash(sample_event)
    is_valid = verify_hash(sample_event, event_hash)

    assert is_valid is True


def test_tamper_detection():
    """Test that modifying an event field causes verification to fail."""
    original_event = {
        "alert_id": "ALT-2026-0093",
        "attack_type": "UNAUTHORIZED_ACCESS",
        "risk_score": 75,
        "severity": "MEDIUM",
    }
    original_hash = generate_hash(original_event)

    # Tamper with the event by changing a field (risk_score)
    tampered_event = original_event.copy()
    tampered_event["risk_score"] = 20

    is_valid = verify_hash(tampered_event, original_hash)

    assert is_valid is False
