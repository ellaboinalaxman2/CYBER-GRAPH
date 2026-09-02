# app/api/routes/mitre.py
from fastapi import APIRouter, HTTPException
from app.api.controllers.mitre_controller import MitreController
from typing import List, Dict

router = APIRouter(prefix="/api/mitre", tags=["MITRE"])

@router.get("/techniques", response_model=List[Dict])
async def get_mitre_techniques():
    return await MitreController.get_mitre_techniques()

@router.get("/techniques/{technique_id}", response_model=Dict)
async def get_mitre_technique(technique_id: str):
    return await MitreController.get_mitre_technique(technique_id)