# app/api/routes/health.py
from fastapi import APIRouter
from app.config.database import MongoDB
from app.config.neo4j import Neo4jDB
from app.config.blockchain import BlockchainClient
import httpx
from app.config.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    return {"status": "healthy"}

@router.get("/services")
async def services_health():
    status = {
        "backend": "healthy",
        "mongodb": "unhealthy",
        "neo4j": "unhealthy",
        "ai_engine": "unhealthy",
        "attack_engine": "unhealthy",
        "blockchain": "unhealthy"
    }
    # Check MongoDB
    try:
        if MongoDB.get_db():
            await MongoDB.get_db().command("ping")
            status["mongodb"] = "healthy"
    except:
        pass
    # Check Neo4j
    try:
        if Neo4jDB.get_driver():
            async with Neo4jDB.get_driver().session() as session:
                await session.run("RETURN 1")
            status["neo4j"] = "healthy"
    except:
        pass
    # Check Blockchain (Web3)
    if BlockchainClient.get_w3() and BlockchainClient.get_w3().is_connected():
        status["blockchain"] = "healthy"
    # Check external services via simple ping (optional)
    # ...
    return status