# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.database import MongoDB
from app.config.neo4j import Neo4jDB
from app.config.blockchain import BlockchainClient
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_middleware import ErrorMiddleware
from app.api.routes import auth, events, nodes, alerts, attack_paths, risk, statistics, mitre, blockchain, health, uploads, graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await MongoDB.connect()
    await Neo4jDB.connect()
    BlockchainClient.connect()
    yield
    # Shutdown
    await MongoDB.close()
    await Neo4jDB.close()
    # Blockchain client may not need close

app = FastAPI(title="Cyber Graph Backend", version="1.0.0", lifespan=lifespan)

# Custom middleware
app.add_middleware(ErrorMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# CORS must be outermost so browser preflight and API error responses retain
# CORS headers. Middleware executes in reverse registration order in FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(nodes.router)
app.include_router(alerts.router)
app.include_router(attack_paths.router)
app.include_router(attack_paths.compat_router)
app.include_router(risk.router)
app.include_router(statistics.router)
app.include_router(mitre.router)
app.include_router(blockchain.router)
app.include_router(health.router)
app.include_router(uploads.router)
app.include_router(graph.router)

@app.get("/")
async def root():
    return {"message": "Cyber Graph Backend is running"}
