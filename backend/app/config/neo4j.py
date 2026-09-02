# app/config/neo4j.py
from neo4j import AsyncGraphDatabase
from app.config.settings import settings

class Neo4jDB:
    driver = None

    @classmethod
    async def connect(cls):
        try:
            cls.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            await cls.driver.verify_connectivity()
            print("Neo4j connected")
        except Exception as e:
            print(f"Neo4j connection failed: {e}")
            cls.driver = None

    @classmethod
    async def close(cls):
        if cls.driver:
            await cls.driver.close()
            print("Neo4j disconnected")

    @classmethod
    def get_driver(cls):
        return cls.driver