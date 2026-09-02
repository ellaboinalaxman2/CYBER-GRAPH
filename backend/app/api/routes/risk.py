# app/api/routes/risk.py
from fastapi import APIRouter, HTTPException, Query
from app.api.controllers.risk_controller import RiskController
from typing import List, Dict

router = APIRouter(prefix="/api/risk", tags=["Risk"])

@router.get("/", response_model=List[Dict])
async def get_risks(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return await RiskController.get_risks(skip, limit)

@router.post("/")
async def create_risk(risk_data: dict):
    return await RiskController.create_risk(risk_data)