# app/api/controllers/statistics_controller.py
from fastapi import HTTPException, status
from app.config.database import MongoDB

class StatisticsController:
    @staticmethod
    async def get_statistics():
        if not MongoDB.get_db():
            return {
                "total_events": 0,
                "total_alerts": 0,
                "total_nodes": 0,
                "database_connected": False
            }
        
        # Get basic statistics
        total_events = await MongoDB.get_db().events.count_documents({})
        total_alerts = await MongoDB.get_db().alerts.count_documents({})
        total_nodes = await MongoDB.get_db().nodes.count_documents({})
        
        return {
            "total_events": total_events,
            "total_alerts": total_alerts,
            "total_nodes": total_nodes,
            "database_connected": True
        }
