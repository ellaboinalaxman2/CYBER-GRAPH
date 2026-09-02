# app/services/node_service.py
from fastapi import HTTPException, status
from app.config.database import MongoDB
from typing import List

class NodeService:
    @staticmethod
    async def get_nodes(skip: int = 0, limit: int = 100):
        if not MongoDB.get_db():
            return []
        
        cursor = MongoDB.get_db().nodes.find().skip(skip).limit(limit)
        nodes = await cursor.to_list(length=limit)
        return nodes

    @staticmethod
    async def create_node(node_data: dict):
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        result = await MongoDB.get_db().nodes.insert_one(node_data)
        node_data["id"] = str(result.inserted_id)
        return node_data

    @staticmethod
    async def get_node(node_id: str):
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        try:
            from bson import ObjectId
            node = await MongoDB.get_db().nodes.find_one({"_id": ObjectId(node_id)})
            if not node:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
            return node
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid node ID")
