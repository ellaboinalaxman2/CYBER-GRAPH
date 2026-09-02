"""Tests for Neo4j graph operations."""

import pytest
from src.neo4j.repositories.node_repository import NodeRepository
from src.neo4j.repositories.graph_repository import GraphRepository
from src.neo4j.seeds.seed_graph import GraphSeeder
from src.core.exceptions import NodeNotFoundError, Neo4jError


class TestNodeRepository:
    """Test node repository operations."""
    
    @pytest.fixture
    def node_repo(self):
        """Create node repository instance."""
        return NodeRepository()
    
    def test_create_node(self, node_repo):
        """Test creating a node."""
        node = node_repo.create_node(
            "TEST-NODE-1",
            "DEVICE",
            {"hostname": "test-device", "ip": "192.168.1.100"}
        )
        assert node["id"] == "TEST-NODE-1"
        assert node["type"] == "DEVICE"
        assert "hostname" in node
    
    def test_get_node(self, node_repo):
        """Test getting a node."""
        # Create first
        node_repo.create_node("TEST-NODE-2", "DEVICE")
        
        # Then get
        node = node_repo.get_node("TEST-NODE-2")
        assert node["id"] == "TEST-NODE-2"
    
    def test_get_node_not_found(self, node_repo):
        """Test getting a non-existent node."""
        with pytest.raises(NodeNotFoundError):
            node_repo.get_node("NONEXISTENT")
    
    def test_delete_node(self, node_repo):
        """Test deleting a node."""
        node_repo.create_node("TEST-NODE-3", "DEVICE")
        result = node_repo.delete_node("TEST-NODE-3")
        assert result is True


class TestGraphRepository:
    """Test graph repository operations."""
    
    @pytest.fixture
    def graph_repo(self):
        """Create graph repository instance."""
        return GraphRepository()
    
    @pytest.fixture
    def node_repo(self):
        """Create node repository instance."""
        return NodeRepository()
    
    def test_create_relationship(self, graph_repo, node_repo):
        """Test creating a relationship."""
        # Create nodes
        node_repo.create_node("NODE-A", "DEVICE")
        node_repo.create_node("NODE-B", "DEVICE")
        
        # Create relationship
        rel = graph_repo.create_relationship(
            "NODE-A",
            "NODE-B",
            "CONNECTS_TO",
            {"protocol": "SSH"}
        )
        assert rel is not None
    
    def test_find_path(self, graph_repo, node_repo):
        """Test finding a path."""
        # Create nodes
        node_repo.create_node("PATH-1", "DEVICE")
        node_repo.create_node("PATH-2", "DEVICE")
        node_repo.create_node("PATH-3", "DEVICE")
        
        # Create relationships
        graph_repo.create_relationship("PATH-1", "PATH-2", "CONNECTS_TO")
        graph_repo.create_relationship("PATH-2", "PATH-3", "CONNECTS_TO")
        
        # Find path
        paths = graph_repo.find_path("PATH-1", "PATH-3")
        assert len(paths) > 0
        assert len(paths[0]["nodes"]) == 3
    
    def test_get_neighbors(self, graph_repo, node_repo):
        """Test getting neighbors."""
        # Create nodes
        node_repo.create_node("NEIGHBOR-1", "DEVICE")
        node_repo.create_node("NEIGHBOR-2", "DEVICE")
        
        # Create relationship
        graph_repo.create_relationship("NEIGHBOR-1", "NEIGHBOR-2", "CONNECTS_TO")
        
        # Get neighbors
        neighbors = graph_repo.get_neighbors("NEIGHBOR-1")
        assert len(neighbors) > 0
        assert neighbors[0]["id"] == "NEIGHBOR-2"


class TestGraphSeeder:
    """Test graph seeder."""
    
    def test_seed(self):
        """Test seeding the graph."""
        seeder = GraphSeeder()
        results = seeder.seed()
        
        assert results["nodes_created"] > 0
        assert results["relationships_created"] > 0
        assert len(results["errors"]) == 0
    
    def test_clear_graph(self):
        """Test clearing the graph."""
        seeder = GraphSeeder()
        result = seeder.clear_graph()
        assert result is True