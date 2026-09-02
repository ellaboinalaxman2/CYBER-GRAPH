import asyncio
import sys
sys.path.insert(0, '.')

async def test_routes_debug():
    from app.config.database import MongoDB
    from app.config.neo4j import Neo4jDB
    from app.config.settings import settings
    
    print("Testing database connections...")
    await MongoDB.connect()
    await Neo4jDB.connect()
    
    print("\nTesting routes with full exception tracing...")
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    routes = ['/api/alerts/']
    for route in routes:
        try:
            print(f"\n>>> Testing {route}...")
            response = client.get(route)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            import traceback
            print(f"Exception: {e}")
            traceback.print_exc()

asyncio.run(test_routes_debug())
