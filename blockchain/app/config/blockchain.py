"""Blockchain configuration and Web3 connection module for Cyber Graph."""

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract.contract import Contract

# Determine project root directory (root of the blockchain module)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
ABI_FILE = BASE_DIR / "abi" / "CyberGraphAudit.json"

# Load environment variables from .env
load_dotenv(dotenv_path=ENV_FILE, override=True)


class BlockchainConfig:
    """Encapsulates Web3 connection, account signer, and contract instance."""

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        private_key: Optional[str] = None,
        contract_address: Optional[str] = None,
        abi_path: Optional[Path] = None,
    ) -> None:
        # Load from explicit arguments if provided (including empty strings), else from environment
        self.rpc_url = rpc_url if rpc_url is not None else os.getenv("BLOCKCHAIN_RPC_URL")
        self._private_key = (
            private_key if private_key is not None else os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        )
        self.contract_address = (
            contract_address
            if contract_address is not None
            else os.getenv("CONTRACT_ADDRESS")
        )
        self.abi_path = abi_path or ABI_FILE

        self._validate_inputs()

        # Connect to Ethereum / Anvil RPC node
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(
                f"Failed to connect to blockchain RPC at '{self.rpc_url}'. Ensure Anvil or Ethereum node is running."
            )

        # Initialize Account from private key without exposing the key
        try:
            self.account: LocalAccount = self.w3.eth.account.from_key(self._private_key)
        except Exception as e:
            raise ValueError(f"Invalid BLOCKCHAIN_PRIVATE_KEY provided: {e}") from e

        # Load ABI
        self.abi = self._load_abi(self.abi_path)

        # Checksum the contract address
        try:
            self.checksum_address = self.w3.to_checksum_address(self.contract_address)
        except Exception as e:
            raise ValueError(
                f"Invalid CONTRACT_ADDRESS '{self.contract_address}': {e}"
            ) from e

        # Initialize Web3 Contract instance
        self.contract: Contract = self.w3.eth.contract(
            address=self.checksum_address,
            abi=self.abi,
        )

    def _validate_inputs(self) -> None:
        """Validate required configuration parameters."""
        if not self.rpc_url or not self.rpc_url.strip():
            raise ValueError(
                "Missing configuration: BLOCKCHAIN_RPC_URL is not set in environment or arguments."
            )
        if not self._private_key or not self._private_key.strip():
            raise ValueError(
                "Missing configuration: BLOCKCHAIN_PRIVATE_KEY is not set in environment or arguments."
            )
        if not self.contract_address or not self.contract_address.strip():
            raise ValueError(
                "Missing configuration: CONTRACT_ADDRESS is not set in environment or arguments."
            )

    @staticmethod
    def _load_abi(path: Path) -> list:
        """Load contract ABI JSON from disk."""
        if not path.exists():
            raise FileNotFoundError(f"Contract ABI file not found at: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse ABI JSON from {path}: {e}") from e

    @property
    def account_address(self) -> str:
        """Return the public address of the configured account."""
        return self.account.address


# Singleton / cached instance helper
_blockchain_instance: Optional[BlockchainConfig] = None


def get_blockchain_config(reload: bool = False) -> BlockchainConfig:
    """Retrieve or initialize the singleton BlockchainConfig instance.

    Args:
        reload: If True, reloads the configuration and creates a fresh connection.

    Returns:
        BlockchainConfig: Configured blockchain connection object.
    """
    global _blockchain_instance
    if _blockchain_instance is None or reload:
        _blockchain_instance = BlockchainConfig()
    return _blockchain_instance


def get_web3() -> Web3:
    """Return the active Web3 instance."""
    return get_blockchain_config().w3


def get_account() -> LocalAccount:
    """Return the active LocalAccount."""
    return get_blockchain_config().account


def get_contract() -> Contract:
    """Return the active Web3 Contract instance."""
    return get_blockchain_config().contract
