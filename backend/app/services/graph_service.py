# app/services/graph_service.py
from fastapi import HTTPException, status
from app.config.neo4j import Neo4jDB

class GraphService:
    @staticmethod
    async def get_graph_data():
        driver = Neo4jDB.get_driver()
        if not driver:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Neo4j not connected")
        
        try:
            async with driver.session() as session:
                result = await session.run("MATCH (n) RETURN n LIMIT 100")
                records = await result.data()
                return records
        except Exception:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Neo4j query failed")

    @staticmethod
    async def create_node(label: str, properties: dict):
        driver = Neo4jDB.get_driver()
        if not driver:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Neo4j not connected")
        
        try:
            async with driver.session() as session:
                query = f"CREATE (n:{label} $props) RETURN n"
                result = await session.run(query, props=properties)
                record = await result.single()
                return record["n"]
        except Exception:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Neo4j query failed")
