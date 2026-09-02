"""Integration tests for the complete Cyber Graph blockchain audit and tamper-detection flow."""

import uuid
from app.hashing.hash_service import generate_hash
from app.services.audit_service import AuditService
from app.services.blockchain_service import BlockchainService


def test_complete_blockchain_audit_flow():
    """Test end-to-end security event registration, on-chain lookup, and integrity verification."""
    # 1. Create a sample cybersecurity event
    audit_id = "ALT-001"
    event_id = "EVT-001"
    event = {
        "audit_id": audit_id,
        "event_id": event_id,
        "attack_type": "Brute Force",
        "risk_score": 94,
        "severity": "critical",
    }

    # 2. Generate the SHA-256 hash using the existing hashing service
    expected_event_hash = generate_hash(event)
    assert len(expected_event_hash) == 64

    audit_service = AuditService()
    blockchain_service = BlockchainService()

    # Fallback to unique audit_id if ALT-001 was already registered on the persistent local chain
    try:
        existing = blockchain_service.get_audit(audit_id)
        if existing and existing.get("audit_id") == audit_id:
            audit_id = f"ALT-001-{uuid.uuid4().hex[:6]}"
            event["audit_id"] = audit_id
            expected_event_hash = generate_hash(event)
    except Exception:
        pass

    # 3. Register the event using AuditService
    result = audit_service.register_security_event(
        event=event,
        audit_id=audit_id,
        event_id=event_id,
    )

    # 4. Verify that a transaction hash is returned
    assert "transaction_hash" in result
    assert result["transaction_hash"] is not None
    assert result["transaction_hash"].startswith("0x")

    # 5. Verify that a block number is returned
    assert "block_number" in result
    assert isinstance(result["block_number"], int)
    assert result["block_number"] > 0

    # 6. Retrieve the record from the smart contract
    retrieved_record = blockchain_service.get_audit(audit_id)

    # 7. Confirm audit ID, event ID, and event hash match
    assert retrieved_record["audit_id"] == audit_id
    assert retrieved_record["event_id"] == event_id
    assert retrieved_record["event_hash"] == expected_event_hash
    assert retrieved_record["event_hash"] == result["event_hash"]

    # 8. Verify the event using verify_audit() (Expected: True)
    is_valid = blockchain_service.verify_audit(audit_id, expected_event_hash)
    assert is_valid is True

    # Also verify through AuditService integrity check
    assert audit_service.verify_security_event(audit_id, event) is True


def test_blockchain_tamper_detection():
    """Test on-chain tamper detection when an event field is altered after registration."""
    audit_service = AuditService()
    blockchain_service = BlockchainService()

    audit_id = f"ALT-TAMPER-{uuid.uuid4().hex[:8]}"
    event_id = f"EVT-TAMPER-{uuid.uuid4().hex[:8]}"

    # 1. Create an original security event
    original_event = {
        "audit_id": audit_id,
        "event_id": event_id,
        "attack_type": "SQL_INJECTION",
        "risk_score": 88,
        "severity": "high",
        "endpoint": "/api/v1/auth/login",
    }

    # 2. Generate its SHA-256 hash
    original_hash = generate_hash(original_event)
    assert len(original_hash) == 64

    # 3. Register it on the blockchain
    reg_result = audit_service.register_security_event(
        event=original_event,
        audit_id=audit_id,
        event_id=event_id,
    )
    assert reg_result["transaction_hash"].startswith("0x")
    assert reg_result["event_hash"] == original_hash

    # 4. Create a modified version of the same event by changing one field (risk_score)
    modified_event = original_event.copy()
    modified_event["risk_score"] = 15

    # 5. Generate the SHA-256 hash of the modified event
    modified_hash = generate_hash(modified_event)
    assert modified_hash != original_hash

    # 6. Verify the modified hash against the original blockchain record
    is_modified_valid = blockchain_service.verify_audit(audit_id, modified_hash)

    # 7. Assert that verification returns False
    assert is_modified_valid is False
    assert audit_service.verify_security_event(audit_id, modified_event) is False

    # Also test that the original unchanged event still verifies successfully (Expected: True)
    is_original_valid = blockchain_service.verify_audit(audit_id, original_hash)
    assert is_original_valid is True
    assert audit_service.verify_security_event(audit_id, original_event) is True
