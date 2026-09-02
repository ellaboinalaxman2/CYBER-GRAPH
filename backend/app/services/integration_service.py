# app/services/integration_service.py
from fastapi import HTTPException, status
from app.config.database import MongoDB

class IntegrationService:
    @staticmethod
    async def get_integrations():
        if not MongoDB.get_db():
            return []
        
        integrations = await MongoDB.get_db().integrations.find().to_list(length=100)
        return integrations

    @staticmethod
    async def create_integration(integration_data: dict):
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        result = await MongoDB.get_db().integrations.insert_one(integration_data)
        integration_data["id"] = str(result.inserted_id)
        return integration_data
