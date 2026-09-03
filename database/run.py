import uvicorn

from src.core.config import settings


if __name__ == "__main__":

    print()
    print("=" * 60)
    print(" CYBER-GRAPH DATABASE ENGINE")
    print("=" * 60)
    print(
        f" Host       : {settings.api_host}"
    )
    print(
        f" Port       : {settings.api_port}"
    )
    print(
        f" Neo4j URI  : {settings.neo4j_uri}"
    )
    print("=" * 60)
    print()

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )