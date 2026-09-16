import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mongodb.config.connection import mongodb_connection
from neo4j.config.connection import neo4j_connection

def health_check():
    """Check health of all database connections"""
    
    print("=" * 60)
    print("Health Check")
    print("=" * 60)
    
    status = {
        "mongodb": {
            "connected": False,
            "stats": {}
        },
        "neo4j": {
            "connected": False,
            "stats": {}
        }
    }
    
    # Check MongoDB
    print("\n[1/2] Checking MongoDB...")
    try:
        status["mongodb"]["connected"] = mongodb_connection.health_check()
        if status["mongodb"]["connected"]:
            status["mongodb"]["stats"] = mongodb_connection.get_stats()
            print(f"✅ MongoDB: Connected")
            print(f"   Database: {status['mongodb']['stats'].get('database')}")
            print(f"   Collections: {status['mongodb']['stats'].get('collections')}")
        else:
            print("❌ MongoDB: Connection failed")
    except Exception as e:
        print(f"❌ MongoDB: Error - {e}")
    
    # Check Neo4j
    print("\n[2/2] Checking Neo4j...")
    try:
        status["neo4j"]["connected"] = neo4j_connection.health_check()
        if status["neo4j"]["connected"]:
            status["neo4j"]["stats"] = neo4j_connection.get_stats()
            print(f"✅ Neo4j: Connected")
            print(f"   Database: {status['neo4j']['stats'].get('database')}")
            print(f"   Nodes: {status['neo4j']['stats'].get('nodes')}")
            print(f"   Relationships: {status['neo4j']['stats'].get('relationships')}")
        else:
            print("❌ Neo4j: Connection failed")
    except Exception as e:
        print(f"❌ Neo4j: Error - {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Health Check Summary")
    print("=" * 60)
    all_healthy = status["mongodb"]["connected"] and status["neo4j"]["connected"]
    print(f"Status: {'✅ Healthy' if all_healthy else '❌ Issues Detected'}")
    
    return status

def health_check_report():
    """Generate detailed health check report"""
    status = health_check()
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy" if status["mongodb"]["connected"] and status["neo4j"]["connected"] else "unhealthy",
        "checks": status
    }
    
    # Save report
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"health_check_{timestamp}.json"
    
    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    return report

if __name__ == "__main__":
    health_check()