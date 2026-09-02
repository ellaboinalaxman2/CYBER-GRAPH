"""Tests for AuditService end-to-end event hashing, registration, and integrity verification."""

import uuid
import pytest
from app.services.audit_service import AuditService, register_security_event


@pytest.fixture
def audit_service():
    """Fixture providing an instance of AuditService."""
    return AuditService()


def test_register_security_event(audit_service):
    """Verify that a security event dictionary is hashed and registered on-chain."""
    event_id = f"EVT-ALERT-{uuid.uuid4().hex[:6]}"
    sample_event = {
        "event_id": event_id,
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.5",
        "attack_type": "PORT_SCAN",
        "risk_score": 60,
        "timestamp": "2026-08-30T22:05:00Z",
    }

    result = audit_service.register_security_event(sample_event)

    assert "audit_id" in result and result["audit_id"].startswith("AUD-")
    assert result["event_id"] == event_id
    assert len(result["event_hash"]) == 64
    assert result["transaction_hash"].startswith("0x")
    assert isinstance(result["block_number"], int)

    # Verify on-chain retrieval
    stored_record = audit_service.get_audit_record(result["audit_id"])
    assert stored_record["audit_id"] == result["audit_id"]
    assert stored_record["event_id"] == event_id
    assert stored_record["event_hash"] == result["event_hash"]


def test_verify_security_event_end_to_end(audit_service):
    """Verify integrity of original vs tampered events against on-chain records."""
    event_id = f"EVT-ALERT-{uuid.uuid4().hex[:6]}"
    original_event = {
        "event_id": event_id,
        "user": "admin",
        "action": "privilege_escalation",
        "status": "blocked",
    }

    reg_result = audit_service.register_security_event(original_event)
    audit_id = reg_result["audit_id"]

    # 1. Verification of original unchanged event must pass
    assert audit_service.verify_security_event(audit_id, original_event) is True

    # 2. Verification of tampered event must fail
    tampered_event = original_event.copy()
    tampered_event["status"] = "allowed"
    assert audit_service.verify_security_event(audit_id, tampered_event) is False


def test_convenience_register_function():
    """Verify the top-level register_security_event helper function."""
    event_id = f"EVT-ALERT-{uuid.uuid4().hex[:6]}"
    event = {
        "alert_id": event_id,
        "threat": "MALWARE_INFECTION",
        "severity": "CRITICAL",
    }
    result = register_security_event(event)

    assert result["event_id"] == event_id
    assert len(result["event_hash"]) == 64
    assert result["transaction_hash"].startswith("0x")
    assert isinstance(result["block_number"], int)
