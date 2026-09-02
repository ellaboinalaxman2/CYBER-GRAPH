import asyncio
import sys
sys.path.insert(0, '.')

async def test_routes():
    from app.config.database import MongoDB
    from app.config.neo4j import Neo4jDB
    from app.config.settings import settings
    
    print("Testing database connections...")
    try:
        await MongoDB.connect()
        db = MongoDB.get_db()
        print(f"MongoDB connection: {'✓' if db else '✗'}")
    except Exception as e:
        print(f"MongoDB error: {e}")
    
    try:
        await Neo4jDB.connect()
        driver = Neo4jDB.get_driver()
        print(f"Neo4j connection: {'✓' if driver else '✗'}")
    except Exception as e:
        print(f"Neo4j error: {e}")
    
    print("\nTesting routes...")
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    routes = ['/api/graph', '/api/alerts/', '/api/attack-paths/', '/api/attacks']
    for route in routes:
        try:
            response = client.get(route)
            print(f"GET {route} -> {response.status_code}")
            if response.status_code >= 400:
                try:
                    print(f"  Response: {response.json()}")
                except:
                    print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"GET {route} -> Error: {str(e)[:100]}")

asyncio.run(test_routes())
