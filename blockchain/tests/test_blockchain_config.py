"""Tests for Blockchain Web3 connection, account loading, and contract initialization."""

import pytest
from app.config.blockchain import (
    BlockchainConfig,
    get_account,
    get_blockchain_config,
    get_contract,
    get_web3,
)


def test_blockchain_connection():
    """Verify Web3 connection to Anvil local node."""
    config = get_blockchain_config(reload=True)
    assert config.w3.is_connected() is True
    assert get_web3().is_connected() is True


def test_account_loading():
    """Verify that the account signer is initialized and has a valid address."""
    account = get_account()
    assert account is not None
    assert account.address.startswith("0x")
    assert len(account.address) == 42


def test_contract_initialization():
    """Verify that the CyberGraphAudit contract instance is initialized with its ABI functions."""
    contract = get_contract()
    assert contract is not None
    assert contract.address.startswith("0x")

    # Verify functions are exposed on the Web3 contract
    assert hasattr(contract.functions, "registerAudit")
    assert hasattr(contract.functions, "getAudit")
    assert hasattr(contract.functions, "verifyAudit")


def test_contract_view_call():
    """Verify a read call against the deployed contract on Anvil."""
    contract = get_contract()
    # verifyAudit on an unregistered ID should return False without reverting
    is_valid = contract.functions.verifyAudit(
        "NON_EXISTENT_AUDIT_ID",
        "0000000000000000000000000000000000000000000000000000000000000000",
    ).call()
    assert is_valid is False


def test_missing_config_validation():
    """Verify that missing configuration parameters raise clear ValueErrors."""
    with pytest.raises(ValueError, match="BLOCKCHAIN_RPC_URL"):
        BlockchainConfig(rpc_url="")

    with pytest.raises(ValueError, match="BLOCKCHAIN_PRIVATE_KEY"):
        BlockchainConfig(rpc_url="http://127.0.0.1:8545", private_key="")

    with pytest.raises(ValueError, match="CONTRACT_ADDRESS"):
        BlockchainConfig(
            rpc_url="http://127.0.0.1:8545",
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            contract_address="",
        )
