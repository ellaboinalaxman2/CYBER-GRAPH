from .seed_nodes import seed_nodes
from .seed_relationships import seed_relationships

def seed_all():
    """Seed all data into Neo4j"""
    
    print("=" * 60)
    print("Seeding Neo4j with complete data")
    print("=" * 60)
    
    # Seed nodes
    print("\n[1/2] Seeding nodes...")
    nodes = seed_nodes()
    print(f"Seeded {len(nodes)} nodes")
    
    # Seed relationships
    print("\n[2/2] Seeding relationships...")
    relationships = seed_relationships()
    print(f"Seeded {len(relationships)} relationships")
    
    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)
    
    # Get final statistics
    from ..repositories.graph_repository import GraphRepository
    graph_repo = GraphRepository()
    stats = graph_repo.get_graph_statistics()
    
    print("\nFinal Graph Statistics:")
    print(f"  Total Nodes: {stats.get('total_nodes', 0)}")
    print(f"  Total Relationships: {stats.get('total_relationships', 0)}")
    print(f"  Average Degree: {stats.get('avg_degree', 0):.2f}")
    print(f"  Average Criticality: {stats.get('avg_criticality', 0):.2f}")

if __name__ == "__main__":
    seed_all()