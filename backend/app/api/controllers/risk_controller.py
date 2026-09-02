# app/api/controllers/risk_controller.py
from fastapi import HTTPException, status
from app.config.database import MongoDB
from typing import List

class RiskController:
    @staticmethod
    async def get_risks(skip: int = 0, limit: int = 100):
        if not MongoDB.get_db():
            return []
        
        cursor = MongoDB.get_db().risks.find().skip(skip).limit(limit)
        risks = await cursor.to_list(length=limit)
        return risks

    @staticmethod
    async def create_risk(risk_data: dict):
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        result = await MongoDB.get_db().risks.insert_one(risk_data)
        risk_data["id"] = str(result.inserted_id)
        return risk_data
