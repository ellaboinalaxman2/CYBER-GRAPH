# app/api/controllers/blockchain_controller.py
from fastapi import HTTPException, status
from app.config.blockchain import BlockchainClient

class BlockchainController:
    @staticmethod
    async def get_blockchain_status():
        w3 = BlockchainClient.get_w3()
        if not w3:
            return {"status": "not_connected"}
        
        try:
            if w3.is_connected():
                return {
                    "status": "connected",
                    "block_number": w3.eth.block_number,
                    "chain_id": w3.eth.chain_id
                }
            else:
                return {"status": "disconnected"}
        except Exception:
            return {"status": "error"}

    @staticmethod
    async def get_transaction(tx_hash: str):
        w3 = BlockchainClient.get_w3()
        if not w3 or not w3.is_connected():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Blockchain not connected")
        
        try:
            tx = w3.eth.get_transaction(tx_hash)
            return tx
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
