"""Graph repository for Neo4j operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import Neo4jError
from src.neo4j.connection import neo4j
from src.neo4j.repositories.node_repository import NodeRepository


class GraphRepository:
    """
    Repository for graph operations in Neo4j.

    Features:
    - Create relationships
    - Find paths
    - Get neighbors
    - Graph statistics
    - Attack path reconstruction
    """

    ALLOWED_RELATIONSHIPS = {
        "CONNECTS_TO",
        "ACCESSES",
        "AUTHENTICATES_TO",
        "RUNS",
        "COMMUNICATES_WITH",
        "DEPENDS_ON",
        "TALKS_TO",
        "ATTACKS",
        "COMPROMISES",
        "LATERAL_MOVEMENT",
    }

    def __init__(self):
        """Initialize graph repository."""

        self.logger = get_logger(
            "neo4j.graph_repository"
        )

        self.node_repo = NodeRepository()

        if neo4j.is_connected():
            self._ensure_indexes()

    # ============================================================
    # INDEXES
    # ============================================================

    def _ensure_indexes(self) -> None:
        """Create Neo4j indexes."""

        try:

            neo4j.execute_query(
                """
                CREATE CONSTRAINT IF NOT EXISTS
                FOR (n:Node)
                REQUIRE n.id IS UNIQUE
                """
            )

            neo4j.execute_query(
                """
                CREATE INDEX IF NOT EXISTS
                FOR (n:Node)
                ON (n.type)
                """
            )

            neo4j.execute_query(
                """
                CREATE INDEX IF NOT EXISTS
                FOR (n:Node)
                ON (n.created_at)
                """
            )

            self.logger.info(
                "Neo4j graph indexes initialized"
            )

        except Exception as e:

            self.logger.error(
                f"Failed to create graph indexes: {e}"
            )

    # ============================================================
    # CREATE RELATIONSHIP
    # ============================================================

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create or update a relationship.

        MERGE prevents duplicate relationships.
        """

        if not neo4j.is_connected():

            raise Neo4jError(
                "Neo4j is not connected"
            )

        source_id = str(source_id).strip()
        target_id = str(target_id).strip()

        if not source_id:
            raise Neo4jError(
                "Source node ID cannot be empty"
            )

        if not target_id:
            raise Neo4jError(
                "Target node ID cannot be empty"
            )

        relationship_type = (
            str(relationship_type)
            .upper()
            .strip()
        )

        if (
            relationship_type
            not in self.ALLOWED_RELATIONSHIPS
        ):

            raise Neo4jError(
                f"Invalid relationship type: "
                f"{relationship_type}"
            )

        properties = properties or {}

        properties = {
            key: value
            for key, value in properties.items()
            if value is not None
        }

        # --------------------------------------------------------
        # Make sure nodes exist
        # --------------------------------------------------------

        try:

            self.node_repo.get_node(
                source_id
            )

        except Exception as e:

            raise Neo4jError(
                f"Source node not found: "
                f"{source_id}"
            ) from e

        try:

            self.node_repo.get_node(
                target_id
            )

        except Exception as e:

            raise Neo4jError(
                f"Target node not found: "
                f"{target_id}"
            ) from e

        # --------------------------------------------------------
        # Relationship query
        # --------------------------------------------------------

        now = (
            datetime.utcnow().isoformat()
            + "Z"
        )

        # relationship_type is safe because it
        # comes from the allowlist above.

        query = f"""
        MATCH (a:Node {{id: $source_id}})
        MATCH (b:Node {{id: $target_id}})

        MERGE (a)-[r:{relationship_type}]->(b)

        ON CREATE SET
            r.created_at = $created_at

        SET
            r.updated_at = $updated_at,
            r += $properties

        RETURN a, b, r
        """

        parameters = {
            "source_id": source_id,
            "target_id": target_id,
            "created_at": now,
            "updated_at": now,
            "properties": properties,
        }

        try:

            result = neo4j.execute_query(
                query,
                parameters,
            )

            if not result:

                raise Neo4jError(
                    "Relationship was not created"
                )

            self.logger.info(
                f"Created/updated relationship: "
                f"{source_id} -[{relationship_type}]-> "
                f"{target_id}"
            )

            return {
                "source": result[0].get(
                    "a",
                    {},
                ),
                "target": result[0].get(
                    "b",
                    {},
                ),
                "relationship": result[0].get(
                    "r",
                    {},
                ),
            }

        except Neo4jError:
            raise

        except Exception as e:

            self.logger.error(
                f"Failed to create relationship: {e}"
            )

            raise Neo4jError(
                f"Failed to create relationship: {e}"
            ) from e

    # ============================================================
    # FIND PATH
    # ============================================================

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10,
    ) -> List[Dict[str, Any]]:
        """Find shortest path between two nodes."""

        if not neo4j.is_connected():
            return []

        max_depth = max(
            1,
            min(int(max_depth), 100),
        )

        query = f"""
        MATCH path = shortestPath(
            (a:Node {{id: $source_id}})
            -[*..{max_depth}]-
            (b:Node {{id: $target_id}})
        )

        RETURN path
        """

        parameters = {
            "source_id": source_id,
            "target_id": target_id,
        }

        try:

            result = neo4j.execute_query(
                query,
                parameters,
            )

            paths = []

            for record in result:

                path = record.get(
                    "path"
                )

                if not path:
                    continue

                nodes = [
                    node.get("id")
                    for node in path.nodes
                ]

                relationships = [
                    {
                        "from": rel.start_node.get(
                            "id"
                        ),
                        "to": rel.end_node.get(
                            "id"
                        ),
                        "type": rel.type,
                    }
                    for rel in path.relationships
                ]

                paths.append(
                    {
                        "nodes": nodes,
                        "relationships": relationships,
                        "length": len(nodes) - 1,
                    }
                )

            return paths

        except Exception as e:

            self.logger.error(
                f"Failed to find path: {e}"
            )

            return []

    # ============================================================
    # GET NEIGHBORS
    # ============================================================

    def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        depth: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get neighbors of a node."""

        if not neo4j.is_connected():
            return []

        depth = max(
            1,
            min(int(depth), 20),
        )

        parameters = {
            "node_id": node_id,
        }

        if depth == 1:

            query = """
            MATCH (n:Node {id: $node_id})

            MATCH (n)-[r]-(neighbor:Node)
            """

            if relationship_type:

                relationship_type = (
                    str(relationship_type)
                    .upper()
                    .strip()
                )

                if (
                    relationship_type
                    not in self.ALLOWED_RELATIONSHIPS
                ):

                    raise Neo4jError(
                        f"Invalid relationship type: "
                        f"{relationship_type}"
                    )

                query += """
                WHERE type(r) = $relationship_type
                """

                parameters[
                    "relationship_type"
                ] = relationship_type

            query += """
            RETURN
                neighbor.id AS id,
                neighbor.type AS type,
                collect(type(r)) AS relationship_types
            """

        else:

            query = f"""
            MATCH (n:Node {{id: $node_id}})

            MATCH (n)-[*1..{depth}]-(neighbor:Node)

            WHERE n <> neighbor

            RETURN DISTINCT
                neighbor.id AS id,
                neighbor.type AS type
            """

        try:

            result = neo4j.execute_query(
                query,
                parameters,
            )

            neighbors = []

            for record in result:

                node_id_value = record.get(
                    "id"
                )

                if node_id_value is None:
                    continue

                neighbors.append(
                    {
                        "id": node_id_value,
                        "type": record.get(
                            "type"
                        ),
                        "relationship_types": (
                            record.get(
                                "relationship_types"
                            )
                            or []
                        ),
                    }
                )

            return neighbors

        except Exception as e:

            self.logger.error(
                f"Failed to get neighbors: {e}"
            )

            return []

    # ============================================================
    # GRAPH STATISTICS
    # ============================================================

    def get_graph_statistics(
        self,
    ) -> Dict[str, Any]:
        """Get graph statistics."""

        if not neo4j.is_connected():

            return {
                "status": "offline",
                "message": "Neo4j not connected",
            }

        try:

            # Total nodes

            node_result = neo4j.execute_query(
                """
                MATCH (n:Node)
                RETURN count(n) AS count
                """
            )

            total_nodes = (
                node_result[0].get(
                    "count",
                    0,
                )
                if node_result
                else 0
            )

            # Total relationships

            relationship_result = (
                neo4j.execute_query(
                    """
                    MATCH ()-[r]->()
                    RETURN count(r) AS count
                    """
                )
            )

            total_relationships = (
                relationship_result[0].get(
                    "count",
                    0,
                )
                if relationship_result
                else 0
            )

            # Node types

            node_types_result = (
                neo4j.execute_query(
                    """
                    MATCH (n:Node)

                    RETURN
                        n.type AS type,
                        count(n) AS count

                    ORDER BY count DESC
                    """
                )
            )

            node_types = [
                {
                    "type": record.get(
                        "type"
                    ),
                    "count": record.get(
                        "count"
                    ),
                }
                for record in node_types_result
            ]

            # Relationship types

            relationship_types_result = (
                neo4j.execute_query(
                    """
                    MATCH ()-[r]->()

                    RETURN
                        type(r) AS type,
                        count(r) AS count

                    ORDER BY count DESC
                    """
                )
            )

            relationship_types = [
                {
                    "type": record.get(
                        "type"
                    ),
                    "count": record.get(
                        "count"
                    ),
                }
                for record in relationship_types_result
            ]

            # Most connected nodes

            most_connected_result = (
                neo4j.execute_query(
                    """
                    MATCH (n:Node)

                    OPTIONAL MATCH (n)-[]-()

                    RETURN
                        n.id AS id,
                        n.type AS type,
                        count(*) AS degree

                    ORDER BY degree DESC

                    LIMIT 10
                    """
                )
            )

            most_connected = [
                {
                    "id": record.get(
                        "id"
                    ),
                    "type": record.get(
                        "type"
                    ),
                    "degree": record.get(
                        "degree"
                    ),
                }
                for record in most_connected_result
            ]

            return {
                "status": "healthy",
                "total_nodes": total_nodes,
                "total_relationships": total_relationships,
                "node_types": node_types,
                "relationship_types": relationship_types,
                "most_connected": most_connected,
                "timestamp": (
                    datetime.utcnow()
                    .isoformat()
                    + "Z"
                ),
            }

        except Exception as e:

            self.logger.error(
                f"Failed to get graph statistics: {e}"
            )

            return {
                "status": "error",
                "error": str(e),
            }

    # ============================================================
    # ATTACK PATHS
    # ============================================================

    def get_attack_paths(
        self,
        source_id: str,
        max_depth: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get paths from a source node."""

        if not neo4j.is_connected():
            return []

        max_depth = max(
            1,
            min(int(max_depth), 20),
        )

        query = f"""
        MATCH path =
            (a:Node {{id: $source_id}})
            -[*1..{max_depth}]-
            (target:Node)

        WHERE a <> target

        RETURN
            path,
            length(path) AS length

        ORDER BY length ASC
        """

        parameters = {
            "source_id": source_id,
        }

        try:

            result = neo4j.execute_query(
                query,
                parameters,
            )

            paths = []

            for record in result:

                path = record.get(
                    "path"
                )

                if not path:
                    continue

                paths.append(
                    {
                        "nodes": [
                            node.get("id")
                            for node in path.nodes
                        ],
                        "relationships": [
                            {
                                "from": (
                                    rel.start_node
                                    .get("id")
                                ),
                                "to": (
                                    rel.end_node
                                    .get("id")
                                ),
                                "type": rel.type,
                            }
                            for rel in path.relationships
                        ],
                        "length": record.get(
                            "length",
                            0,
                        ),
                    }
                )

            return paths

        except Exception as e:

            self.logger.error(
                f"Failed to get attack paths: {e}"
            )

            return []