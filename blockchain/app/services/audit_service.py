"""Audit service integrating cryptographic event hashing with blockchain registration."""

import uuid
from typing import Any, Dict, Optional

from app.hashing.hash_service import generate_hash
from app.services.blockchain_service import BlockchainService


class AuditService:
    """Service providing end-to-end event hashing, on-chain registration, and verification."""

    def __init__(self, blockchain_service: Optional[BlockchainService] = None) -> None:
        """Initialize AuditService.

        Args:
            blockchain_service: Optional BlockchainService instance.
        """
        self.blockchain_service = blockchain_service or BlockchainService()

    def register_security_event(
        self,
        event: Dict[str, Any],
        audit_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a security event, generate its canonical SHA-256 hash, and record it on-chain.

        Args:
            event: Security event dictionary.
            audit_id: Optional explicit audit identifier. If omitted, extracted from event or generated.
            event_id: Optional explicit event identifier. If omitted, extracted from event or generated.

        Returns:
            Dict[str, Any]: Details containing audit_id, event_id, event_hash, transaction_hash, and block_number.

        Raises:
            ValueError: If event is empty or not a dict.
            RuntimeError: If blockchain transaction fails.
        """
        if not isinstance(event, dict) or not event:
            raise ValueError("Security event must be a non-empty dictionary.")

        # 1. Generate SHA-256 hash using the existing canonical hashing module
        event_hash = generate_hash(event)

        # 2. Extract or generate event_id
        resolved_event_id = (
            event_id
            or str(event.get("event_id") or event.get("alert_id") or "")
            or f"EVT-{uuid.uuid4().hex[:12].upper()}"
        )

        # 3. Extract or generate audit_id
        resolved_audit_id = (
            audit_id
            or str(event.get("audit_id") or "")
            or f"AUD-{uuid.uuid4().hex[:12].upper()}"
        )

        # 4. Register hash on the deployed smart contract using BlockchainService
        tx_result = self.blockchain_service.register_audit(
            audit_id=resolved_audit_id,
            event_id=resolved_event_id,
            event_hash=event_hash,
        )

        # 5. Return required fields
        return {
            "audit_id": resolved_audit_id,
            "event_id": resolved_event_id,
            "event_hash": event_hash,
            "transaction_hash": tx_result["transaction_hash"],
            "block_number": tx_result["block_number"],
        }

    def verify_security_event(
        self,
        audit_id: str,
        event: Dict[str, Any],
    ) -> bool:
        """Verify the integrity of a security event against the on-chain audit record.

        Args:
            audit_id: Unique audit identifier stored on-chain.
            event: Security event dictionary to verify.

        Returns:
            bool: True if computed hash matches the on-chain recorded hash, False otherwise.
        """
        if not isinstance(event, dict) or not audit_id:
            return False

        computed_hash = generate_hash(event)
        return self.blockchain_service.verify_audit(audit_id, computed_hash)

    def get_audit_record(self, audit_id: str) -> Dict[str, Any]:
        """Retrieve stored audit details for a given audit ID.

        Args:
            audit_id: Unique audit identifier.

        Returns:
            Dict[str, Any]: Stored audit record from the blockchain.
        """
        return self.blockchain_service.get_audit(audit_id)


# Module-level instance helper
_default_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Return a singleton AuditService instance."""
    global _default_audit_service
    if _default_audit_service is None:
        _default_audit_service = AuditService()
    return _default_audit_service


def register_security_event(
    event: Dict[str, Any],
    audit_id: Optional[str] = None,
    event_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience function to register a security event using the default AuditService."""
    return get_audit_service().register_security_event(
        event=event, audit_id=audit_id, event_id=event_id
    )
