# app/config/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            print("MongoDB connected")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            cls.client = None
            cls.db = None

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB disconnected")

    @classmethod
    def get_db(cls):
        return cls.db

# Convenience function
async def get_mongo_db():
    return MongoDB.get_db()