"""Tests for BlockchainService audit registration, retrieval, and verification."""

import uuid
import pytest
from app.hashing.hash_service import generate_hash
from app.services.blockchain_service import BlockchainService


@pytest.fixture
def blockchain_service():
    """Provides an instance of BlockchainService."""
    return BlockchainService()


def test_register_and_get_audit(blockchain_service):
    """Test registering an audit record on-chain and retrieving its stored data."""
    audit_id = f"AUDIT-{uuid.uuid4().hex[:8]}"
    event_id = f"EVT-{uuid.uuid4().hex[:8]}"
    sample_event = {
        "event_id": event_id,
        "event_type": "BRUTE_FORCE_LOGIN",
        "severity": "CRITICAL",
        "timestamp": "2026-08-30T22:00:00Z",
    }
    event_hash = generate_hash(sample_event)

    # 1. Register audit
    result = blockchain_service.register_audit(audit_id, event_id, event_hash)
    assert result["audit_id"] == audit_id
    assert result["status"] == "success"
    assert result["transaction_hash"].startswith("0x")
    assert isinstance(result["block_number"], int)

    # 2. Get audit
    record = blockchain_service.get_audit(audit_id)
    assert record["audit_id"] == audit_id
    assert record["event_id"] == event_id
    assert record["event_hash"] == event_hash
    assert record["submitter"].startswith("0x")
    assert record["timestamp"] > 0


def test_verify_audit_true_and_false(blockchain_service):
    """Test on-chain verification for valid and tampered event hashes."""
    audit_id = f"AUDIT-{uuid.uuid4().hex[:8]}"
    event_id = f"EVT-{uuid.uuid4().hex[:8]}"
    sample_event = {
        "event_id": event_id,
        "event_type": "RANSOMWARE_DETECTION",
        "severity": "HIGH",
    }
    correct_hash = generate_hash(sample_event)

    # Register audit
    blockchain_service.register_audit(audit_id, event_id, correct_hash)

    # Verify with correct hash -> True
    assert blockchain_service.verify_audit(audit_id, correct_hash) is True

    # Verify with incorrect hash -> False
    tampered_event = sample_event.copy()
    tampered_event["severity"] = "LOW"
    tampered_hash = generate_hash(tampered_event)
    assert blockchain_service.verify_audit(audit_id, tampered_hash) is False

    # Verify non-existent audit ID -> False
    assert blockchain_service.verify_audit("NON_EXISTENT_AUDIT_ID", correct_hash) is False


def test_validation_errors(blockchain_service):
    """Test validation errors for empty arguments."""
    with pytest.raises(ValueError, match="audit_id cannot be empty"):
        blockchain_service.register_audit("", "EVT-1", "hash123")

    with pytest.raises(ValueError, match="event_id cannot be empty"):
        blockchain_service.register_audit("AUD-1", "", "hash123")

    with pytest.raises(ValueError, match="event_hash cannot be empty"):
        blockchain_service.register_audit("AUD-1", "EVT-1", "")

    with pytest.raises(ValueError, match="audit_id cannot be empty"):
        blockchain_service.get_audit("")
