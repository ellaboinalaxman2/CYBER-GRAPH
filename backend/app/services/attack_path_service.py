# app/services/attack_path_service.py
from fastapi import HTTPException, status
from app.config.database import MongoDB
from typing import List

class AttackPathService:
    @staticmethod
    async def get_attack_paths(skip: int = 0, limit: int = 100):
        if not MongoDB.get_db():
            return []
        
        cursor = MongoDB.get_db().attack_paths.find().skip(skip).limit(limit)
        paths = await cursor.to_list(length=limit)
        return paths

    @staticmethod
    async def create_attack_path(path_data: dict):
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        result = await MongoDB.get_db().attack_paths.insert_one(path_data)
        path_data["id"] = str(result.inserted_id)
        return path_data
