# app/api/routes/blockchain.py
from fastapi import APIRouter, HTTPException
from app.api.controllers.blockchain_controller import BlockchainController

router = APIRouter(prefix="/api/blockchain", tags=["Blockchain"])

@router.get("/status")
async def get_blockchain_status():
    return await BlockchainController.get_blockchain_status()

@router.get("/transaction/{tx_hash}")
async def get_transaction(tx_hash: str):
    return await BlockchainController.get_transaction(tx_hash)