# app/config/blockchain.py
from web3 import Web3
from app.config.settings import settings

class BlockchainClient:
    w3 = None
    contract = None

    @classmethod
    def connect(cls):
        try:
            if settings.BLOCKCHAIN_RPC_URL:
                cls.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
                if cls.w3.is_connected():
                    print("Blockchain connected")
                    # Optionally load contract
                    # cls.contract = cls.w3.eth.contract(address=..., abi=...)
                else:
                    print("Blockchain connection failed")
                    cls.w3 = None
            else:
                print("Blockchain RPC URL not set, skipping")
        except Exception as e:
            print(f"Blockchain connection error: {e}")
            cls.w3 = None

    @classmethod
    def get_w3(cls):
        return cls.w3