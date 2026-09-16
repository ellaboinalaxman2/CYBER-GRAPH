import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j.config.connection import neo4j_connection

def init_neo4j():
    """Initialize Neo4j with constraints and indexes"""
    
    print("=" * 60)
    print("Initializing Neo4j")
    print("=" * 60)
    
    try:
        # Check connection
        if not neo4j_connection.health_check():
            print("❌ Neo4j connection failed")
            return False
        
        print("✅ Neo4j connection successful")
        
        # Run constraints
        constraints_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "neo4j", "constraints", "uniqueness.cypher"
        )
        
        if os.path.exists(constraints_file):
            with open(constraints_file, 'r') as f:
                constraints_queries = f.read()
            
            # Split into individual queries
            queries = constraints_queries.split(';')
            
            with neo4j_connection.get_session() as session:
                for query in queries:
                    query = query.strip()
                    if query:
                        try:
                            session.run(query)
                            print("✅ Applied constraint/index")
                        except Exception as e:
                            print(f"⚠️ Could not apply constraint (may already exist): {e}")
        
        print("\n✅ Neo4j initialization complete")
        return True
        
    except Exception as e:
        print(f"❌ Neo4j initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_neo4j()