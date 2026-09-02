"""Blockchain service for interacting with the CyberGraphAudit smart contract."""

from typing import Any, Dict, Optional

from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract.contract import Contract
from web3.exceptions import ContractCustomError, ContractLogicError

from app.config.blockchain import BlockchainConfig, get_blockchain_config


class BlockchainService:
    """Service providing high-level audit registration, retrieval, and verification methods."""

    def __init__(self, config: Optional[BlockchainConfig] = None) -> None:
        """Initialize the blockchain service with configuration.

        Args:
            config: Optional BlockchainConfig instance. If None, uses the singleton instance.
        """
        self._config: BlockchainConfig = config or get_blockchain_config()
        self.w3: Web3 = self._config.w3
        self.account: LocalAccount = self._config.account
        self.contract: Contract = self._config.contract

    def register_audit(
        self, audit_id: str, event_id: str, event_hash: str
    ) -> Dict[str, Any]:
        """Register a new cybersecurity audit record on-chain.

        Args:
            audit_id: Unique audit identifier.
            event_id: Associated security event identifier.
            event_hash: SHA-256 hash of the canonicalized event.

        Returns:
            Dict[str, Any]: Transaction execution details including transaction_hash,
                            block_number, and audit_id.

        Raises:
            ValueError: If input arguments are empty.
            RuntimeError: If transaction building, execution, or mining fails.
        """
        if not audit_id or not audit_id.strip():
            raise ValueError("audit_id cannot be empty")
        if not event_id or not event_id.strip():
            raise ValueError("event_id cannot be empty")
        if not event_hash or not event_hash.strip():
            raise ValueError("event_hash cannot be empty")

        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            chain_id = self.w3.eth.chain_id

            # Build transaction using contract function
            tx_data = self.contract.functions.registerAudit(
                audit_id, event_id, event_hash
            )

            tx = tx_data.build_transaction(
                {
                    "from": self.account.address,
                    "nonce": nonce,
                    "chainId": chain_id,
                    "gasPrice": self.w3.eth.gas_price,
                }
            )

            # Sign transaction with local account
            signed_tx = self.account.sign_transaction(tx)

            # Broadcast transaction
            tx_hash_bytes = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = self.w3.to_hex(tx_hash_bytes)

            # Wait for receipt to confirm mining
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)

            if receipt.status != 1:
                raise RuntimeError(
                    f"Transaction reverted on-chain. TxHash: {tx_hash_hex}"
                )

            return {
                "transaction_hash": tx_hash_hex,
                "block_number": receipt.blockNumber,
                "audit_id": audit_id,
                "gas_used": receipt.gasUsed,
                "status": "success",
            }

        except (ContractLogicError, ContractCustomError) as e:
            raise RuntimeError(f"Smart contract error registering audit '{audit_id}': {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to register audit '{audit_id}' on blockchain: {e}") from e

    def get_audit(self, audit_id: str) -> Dict[str, Any]:
        """Retrieve stored audit record details by audit ID.

        Args:
            audit_id: Unique audit identifier to look up.

        Returns:
            Dict[str, Any]: Audit record data (audit_id, event_id, event_hash, timestamp, submitter).

        Raises:
            ValueError: If audit_id is empty.
            RuntimeError: If the record cannot be retrieved or does not exist.
        """
        if not audit_id or not audit_id.strip():
            raise ValueError("audit_id cannot be empty")

        try:
            record = self.contract.functions.getAudit(audit_id).call()
            return {
                "audit_id": record[0],
                "event_id": record[1],
                "event_hash": record[2],
                "timestamp": record[3],
                "submitter": record[4],
            }
        except ContractLogicError as e:
            raise RuntimeError(f"Audit record '{audit_id}' not found or reverted: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve audit '{audit_id}': {e}") from e

    def verify_audit(self, audit_id: str, event_hash: str) -> bool:
        """Verify whether an event hash matches the stored on-chain record for an audit ID.

        Args:
            audit_id: Unique audit identifier.
            event_hash: SHA-256 event hash to verify.

        Returns:
            bool: True if audit exists and hash matches, False otherwise.
        """
        if not audit_id or not event_hash:
            return False

        try:
            is_valid: bool = self.contract.functions.verifyAudit(
                audit_id, event_hash
            ).call()
            return bool(is_valid)
        except Exception:
            return False
