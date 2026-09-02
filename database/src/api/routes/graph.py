"""Graph routes for Member 4 - Database Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.neo4j.repositories.node_repository import NodeRepository
from src.neo4j.repositories.graph_repository import GraphRepository
from src.neo4j.seeds.seed_graph import GraphSeeder
from src.core.exceptions import Neo4jError, NodeNotFoundError

router = APIRouter()
logger = get_logger("api.graph")
node_repo = NodeRepository()
graph_repo = GraphRepository()


@router.post("/nodes")
async def create_node(
    node_id: str = Query(..., description="Node identifier"),
    node_type: str = Query(..., description="Node type"),
    properties: Optional[Dict[str, Any]] = None,
):
    """
    Create a new node.
    
    Args:
        node_id: Node identifier
        node_type: Node type
        properties: Additional properties
        
    Returns:
        dict: Created node
    """
    try:
        result = node_repo.create_node(node_id, node_type, properties)
        return {
            "status": "created",
            "node": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Neo4jError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """
    Get a node by ID.
    
    Args:
        node_id: Node ID
        
    Returns:
        dict: Node data
    """
    try:
        result = node_repo.get_node(node_id)
        return {
            "status": "success",
            "node": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except NodeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/nodes")
async def get_nodes(
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of nodes"),
):
    """
    Get all nodes.
    
    Args:
        node_type: Filter by node type
        limit: Maximum number of nodes
        
    Returns:
        dict: List of nodes
    """
    try:
        nodes = node_repo.get_all_nodes(node_type, limit)
        return {
            "status": "success",
            "nodes": nodes,
            "total": len(nodes),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/nodes/{node_id}")
async def update_node(node_id: str, properties: Dict[str, Any]):
    """
    Update a node's properties.
    
    Args:
        node_id: Node ID
        properties: Properties to update
        
    Returns:
        dict: Updated node
    """
    try:
        result = node_repo.update_node(node_id, properties)
        return {
            "status": "updated",
            "node": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except NodeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """
    Delete a node.
    
    Args:
        node_id: Node ID
        
    Returns:
        dict: Deletion status
    """
    try:
        node_repo.delete_node(node_id)
        return {
            "status": "deleted",
            "node_id": node_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except NodeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/relationships")
async def create_relationship(
    source_id: str = Query(..., description="Source node ID"),
    target_id: str = Query(..., description="Target node ID"),
    relationship_type: str = Query(..., description="Relationship type"),
    properties: Optional[Dict[str, Any]] = None,
):
    """
    Create a relationship between two nodes.
    
    Args:
        source_id: Source node ID
        target_id: Target node ID
        relationship_type: Relationship type
        properties: Relationship properties
        
    Returns:
        dict: Created relationship
    """
    try:
        result = graph_repo.create_relationship(
            source_id, target_id, relationship_type, properties
        )
        return {
            "status": "created",
            "relationship": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Neo4jError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/paths")
async def find_path(
    source_id: str = Query(..., description="Source node ID"),
    target_id: str = Query(..., description="Target node ID"),
    max_depth: int = Query(10, ge=1, le=20, description="Maximum path depth"),
):
    """
    Find paths between two nodes.
    
    Args:
        source_id: Source node ID
        target_id: Target node ID
        max_depth: Maximum path depth
        
    Returns:
        dict: Paths found
    """
    try:
        paths = graph_repo.find_path(source_id, target_id, max_depth)
        return {
            "status": "success",
            "source": source_id,
            "target": target_id,
            "paths": paths,
            "total": len(paths),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/neighbors/{node_id}")
async def get_neighbors(
    node_id: str,
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    depth: int = Query(1, ge=1, le=5, description="Neighbor depth"),
):
    """
    Get neighbors of a node.
    
    Args:
        node_id: Node ID
        relationship_type: Filter by relationship type
        depth: Neighbor depth
        
    Returns:
        dict: Neighbors found
    """
    try:
        neighbors = graph_repo.get_neighbors(node_id, relationship_type, depth)
        return {
            "status": "success",
            "node": node_id,
            "neighbors": neighbors,
            "total": len(neighbors),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/attack-paths/{node_id}")
async def get_attack_paths(
    node_id: str,
    max_depth: int = Query(5, ge=1, le=10, description="Maximum path depth"),
):
    """
    Get attack paths from a node.
    
    Args:
        node_id: Source node ID
        max_depth: Maximum path depth
        
    Returns:
        dict: Attack paths found
    """
    try:
        paths = graph_repo.get_attack_paths(node_id, max_depth)
        return {
            "status": "success",
            "source": node_id,
            "paths": paths,
            "total": len(paths),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/statistics")
async def get_graph_statistics():
    """
    Get graph statistics.
    
    Returns:
        dict: Graph statistics
    """
    try:
        stats = graph_repo.get_graph_statistics()
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Neo4jError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/seed")
async def seed_graph():
    """
    Seed the graph with sample data.
    
    Returns:
        dict: Seeding results
    """
    try:
        seeder = GraphSeeder()
        
        # Clear existing graph
        seeder.clear_graph()
        
        # Seed new data
        results = seeder.seed()
        
        return {
            "status": "seeded",
            "results": results,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed graph: {str(e)}"
        )


@router.post("/seed/clear")
async def clear_graph():
    """
    Clear all nodes and relationships from the graph.
    
    Returns:
        dict: Clear status
    """
    try:
        seeder = GraphSeeder()
        seeder.clear_graph()
        return {
            "status": "cleared",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear graph: {str(e)}"
        )