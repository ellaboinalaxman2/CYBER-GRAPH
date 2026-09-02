# app/api/routes/alerts.py
from fastapi import APIRouter, Query, HTTPException, status
from app.api.controllers.alert_controller import AlertController
from app.config.database import MongoDB
from typing import List, Dict

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("/", response_model=List[Dict])
async def get_alerts(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    if MongoDB.get_db() is None:
        return [{
            "id": "alert-001",
            "title": "Suspicious outbound login burst",
            "severity": "HIGH",
            "status": "OPEN",
            "source": "10.0.0.2",
            "destination": "10.0.0.3",
            "technique": "Credential stuffing",
            "timestamp": "2026-09-02T09:10:00Z"
        }]
    return await AlertController.get_alerts(skip, limit)

@router.post("/")
async def create_alert(alert_data: dict):
    return await AlertController.create_alert(alert_data)