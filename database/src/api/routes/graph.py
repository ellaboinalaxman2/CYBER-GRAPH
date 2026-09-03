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

@router.post("/events")
async def create_event_graph(
    event: Dict[str, Any],
):
    """
    Convert a normalized security event into Neo4j graph data.

    Creates:
        Source Node
        Destination Node
        Relationship between them
    """

    try:
        # ---------------------------------------------------------
        # Check Neo4j
        # ---------------------------------------------------------

        from src.neo4j.connection import neo4j

        if not neo4j.is_connected():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Neo4j is not connected",
            )

        # ---------------------------------------------------------
        # Extract source / destination
        # ---------------------------------------------------------

        source = event.get("source") or {}
        destination = event.get("destination") or {}

        source_id = (
            source.get("hostname")
            or source.get("ip")
        )

        destination_id = (
            destination.get("hostname")
            or destination.get("ip")
        )

        if not source_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Event does not contain source hostname or source IP",
            )

        if not destination_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Event does not contain destination hostname or destination IP",
            )

        # ---------------------------------------------------------
        # Determine node types
        # ---------------------------------------------------------

        source_type = (
            source.get("device_type")
            or "DEVICE"
        )

        destination_type = (
            destination.get("device_type")
            or "SERVER"
        )

        source_type = str(source_type).upper()
        destination_type = str(destination_type).upper()

        valid_node_types = {
            "DEVICE",
            "SERVER",
            "DATABASE",
            "USER",
            "IP",
            "PROCESS",
            "APPLICATION",
            "FIREWALL",
            "WORKSTATION",
            "UNKNOWN",
        }

        if source_type not in valid_node_types:
            source_type = "DEVICE"

        if destination_type not in valid_node_types:
            destination_type = "SERVER"

        # ---------------------------------------------------------
        # Node properties
        # ---------------------------------------------------------

        source_properties = {
            "ip": source.get("ip"),
            "hostname": source.get("hostname"),
            "port": source.get("port"),
            "user": source.get("user"),
        }

        destination_properties = {
            "ip": destination.get("ip"),
            "hostname": destination.get("hostname"),
            "port": destination.get("port"),
            "user": destination.get("user"),
        }

        # Remove None values
        source_properties = {
            k: v
            for k, v in source_properties.items()
            if v is not None
        }

        destination_properties = {
            k: v
            for k, v in destination_properties.items()
            if v is not None
        }

        # ---------------------------------------------------------
        # Create source node
        # ---------------------------------------------------------

        source_node = node_repo.create_node(
            node_id=str(source_id),
            node_type=source_type,
            properties=source_properties,
        )

        # ---------------------------------------------------------
        # Create destination node
        # ---------------------------------------------------------

        destination_node = node_repo.create_node(
            node_id=str(destination_id),
            node_type=destination_type,
            properties=destination_properties,
        )

        # ---------------------------------------------------------
        # Determine relationship
        # ---------------------------------------------------------

        event_type = str(
            event.get("event_type", "")
        ).upper()

        action = str(
            event.get("action", "")
        ).upper()

        if event_type in {
            "LOGIN",
            "LOGIN_SUCCESS",
            "AUTHENTICATION",
        }:
            relationship_type = "AUTHENTICATES_TO"

        elif event_type in {
            "ACCESS",
            "FILE_ACCESS",
            "DATABASE_ACCESS",
        }:
            relationship_type = "ACCESSES"

        elif event_type in {
            "PROCESS_START",
            "PROCESS_EXECUTION",
        }:
            relationship_type = "RUNS"

        elif event_type in {
            "LATERAL_MOVEMENT",
        }:
            relationship_type = "LATERAL_MOVEMENT"

        elif event_type in {
            "ATTACK",
            "INTRUSION",
        }:
            relationship_type = "ATTACKS"

        else:
            relationship_type = "CONNECTS_TO"

        # ---------------------------------------------------------
        # Relationship properties
        # ---------------------------------------------------------

        relationship_properties = {
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "timestamp": str(event.get("timestamp")),
            "protocol": event.get("protocol"),
            "action": action,
            "severity": str(event.get("severity")),
            "source_ip": source.get("ip"),
            "source_port": source.get("port"),
            "destination_ip": destination.get("ip"),
            "destination_port": destination.get("port"),
            "raw_source": event.get("raw_source"),
        }

        # Remove None values
        relationship_properties = {
            k: v
            for k, v in relationship_properties.items()
            if v is not None
        }

        # ---------------------------------------------------------
        # Create relationship
        # ---------------------------------------------------------

        relationship = graph_repo.create_relationship(
            source_id=str(source_id),
            target_id=str(destination_id),
            relationship_type=relationship_type,
            properties=relationship_properties,
        )

        # ---------------------------------------------------------
        # Return
        # ---------------------------------------------------------

        return {
            "status": "stored",
            "event_id": event.get("event_id"),
            "source_node": {
                "id": source_id,
                "type": source_type,
            },
            "destination_node": {
                "id": destination_id,
                "type": destination_type,
            },
            "relationship": {
                "type": relationship_type,
                "source": source_id,
                "target": destination_id,
            },
            "neo4j": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    except HTTPException:
        raise

    except Neo4jError as e:
        logger.error(
            f"Neo4j event storage failed: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except Exception as e:
        logger.exception(
            f"Unexpected graph event error: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph event storage failed: {str(e)}",
        )

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