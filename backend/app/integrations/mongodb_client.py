# app/integrations/mongodb_client.py
from app.config.database import MongoDB

class MongoDBClient:
    @staticmethod
    async def get_client():
        return MongoDB.client
