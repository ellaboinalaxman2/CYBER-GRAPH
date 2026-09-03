# app/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "cybergraph")
    
    # Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_IN = os.getenv("JWT_EXPIRES_IN", "1d")
    # Blockchain
    BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
    BLOCKCHAIN_CONTRACT_ADDRESS = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS", "")
    
    # External services
    INGESTION_ENGINE_URL = os.getenv("INGESTION_ENGINE_URL", "http://localhost:8001")
    AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8002")
    ATTACK_ENGINE_URL = os.getenv("ATTACK_ENGINE_URL", "http://localhost:8004")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))
    # 100 MiB is large enough for full CICIDS/log exports while
    # still providing a server-side guardrail.  It can be increased per
    # deployment through MAX_UPLOAD_BYTES.
    MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(100 * 1024 * 1024)))

settings = Settings()
