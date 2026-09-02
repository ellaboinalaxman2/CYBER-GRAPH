# app/api/routes/statistics.py
from fastapi import APIRouter
from app.api.controllers.statistics_controller import StatisticsController

router = APIRouter(prefix="/api/statistics", tags=["Statistics"])

@router.get("/")
async def get_statistics():
    return await StatisticsController.get_statistics()