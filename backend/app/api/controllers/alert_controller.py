# app/api/controllers/alert_controller.py
from fastapi import HTTPException, status
from app.config.database import MongoDB
from typing import List

class AlertController:
    @staticmethod
    async def get_alerts(skip: int = 0, limit: int = 100):
        if MongoDB.get_db() is None:
            return []
        
        cursor = MongoDB.get_db().alerts.find().skip(skip).limit(limit)
        alerts = await cursor.to_list(length=limit)
        return alerts

    @staticmethod
    async def create_alert(alert_data: dict):
        if MongoDB.get_db() is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        result = await MongoDB.get_db().alerts.insert_one(alert_data)
        alert_data["id"] = str(result.inserted_id)
        return alert_data
