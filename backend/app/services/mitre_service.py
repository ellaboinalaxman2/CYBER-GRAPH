# app/services/mitre_service.py
from fastapi import HTTPException, status
from app.config.database import MongoDB
from typing import List

class MitreService:
    @staticmethod
    async def get_mitre_techniques():
        if not MongoDB.get_db():
            return []
        
        techniques = await MongoDB.get_db().mitre_techniques.find().to_list(length=1000)
        return techniques

    @staticmethod
    async def get_mitre_technique(technique_id: str):
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        technique = await MongoDB.get_db().mitre_techniques.find_one({"technique_id": technique_id})
        if not technique:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technique not found")
        return technique
