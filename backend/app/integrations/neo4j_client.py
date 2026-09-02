# app/integrations/neo4j_client.py
from app.config.neo4j import Neo4jDB

class Neo4jClient:
    @staticmethod
    async def get_driver():
        return Neo4jDB.get_driver()
