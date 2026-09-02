# app/api/routes/nodes.py
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/nodes", tags=["Nodes"])

@router.get("/")
async def get_nodes():
    return {"message": "Nodes endpoint - under construction"}

@router.post("/")
async def create_node():
    return {"message": "Create node endpoint - under construction"}

@router.get("/{node_id}")
async def get_node(node_id: str):
    return {"message": f"Get node {node_id} endpoint - under construction"}
