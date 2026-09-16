import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mongodb.seeds import seed_users, seed_events, seed_alerts
from neo4j.seeds import seed_nodes, seed_relationships

def seed_all():
    """Seed all databases with initial data"""
    
    print("=" * 60)
    print("Seeding All Databases")
    print("=" * 60)
    
    # Seed MongoDB
    print("\n[1/4] Seeding MongoDB users...")
    seed_users()
    
    print("\n[2/4] Seeding MongoDB events...")
    events = seed_events()
    
    print("\n[3/4] Seeding MongoDB alerts...")
    seed_alerts()
    
    # Seed Neo4j
    print("\n[4/4] Seeding Neo4j...")
    from neo4j.seeds.seed_all import seed_all as seed_neo4j_all
    seed_neo4j_all()
    
    print("\n" + "=" * 60)
    print("✅ All databases seeded successfully!")
    print("=" * 60)

if __name__ == "__main__":
    seed_all()