"""Node repository for Neo4j operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import Neo4jError, NodeNotFoundError
from src.neo4j.connection import neo4j


class NodeRepository:
    """
    Repository for node operations in Neo4j.

    Features:
    - Create nodes
    - Read nodes
    - Update nodes
    - Delete nodes
    - Search nodes
    - Node type management
    - Neo4j constraints and indexes
    """

    def __init__(self):
        """Initialize the node repository."""

        self.logger = get_logger(
            "neo4j.node_repository"
        )

        if neo4j.is_connected():
            self._ensure_constraints()
            self._ensure_indexes()
        else:
            self.logger.warning(
                "Neo4j not connected, "
                "skipping constraints and indexes"
            )

    # ============================================================
    # CONSTRAINTS
    # ============================================================

    def _ensure_constraints(self) -> None:
        """Create Neo4j constraints."""

        try:
            neo4j.execute_query(
                """
                CREATE CONSTRAINT IF NOT EXISTS
                FOR (n:Node)
                REQUIRE n.id IS UNIQUE
                """
            )

            self.logger.info(
                "Neo4j node constraints created"
            )

        except Exception as e:
            self.logger.warning(
                f"Failed to create constraints: {e}"
            )

    # ============================================================
    # INDEXES
    # ============================================================

    def _ensure_indexes(self) -> None:
        """Create Neo4j indexes."""

        try:
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
                "Neo4j node indexes created"
            )

        except Exception as e:
            self.logger.warning(
                f"Failed to create indexes: {e}"
            )

    # ============================================================
    # CREATE NODE
    # ============================================================

    def create_node(
        self,
        node_id: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create or update a Neo4j node.

        MERGE is used so that repeated security events
        do not create duplicate nodes.
        """

        if not neo4j.is_connected():
            raise Neo4jError(
                "Neo4j is not connected"
            )

        if not node_id:
            raise Neo4jError(
                "Node ID cannot be empty"
            )

        node_id = str(node_id).strip()

        if not node_id:
            raise Neo4jError(
                "Node ID cannot be empty"
            )

        if not node_type:
            node_type = "UNKNOWN"

        node_type = str(node_type).upper().strip()

        properties = properties or {}

        # Remove None values
        properties = {
            key: value
            for key, value in properties.items()
            if value is not None
        }

        now = (
            datetime.utcnow().isoformat()
            + "Z"
        )

        query = """
        MERGE (n:Node {id: $id})

        ON CREATE SET
            n.created_at = $created_at

        SET
            n.type = $type,
            n.updated_at = $updated_at

        SET n += $properties

        RETURN n
        """

        parameters = {
            "id": node_id,
            "type": node_type,
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
                    f"Failed to create node: {node_id}"
                )

            node_data = result[0].get(
                "n",
                {},
            )

            self.logger.info(
                f"Created/updated node: "
                f"{node_id} "
                f"(type={node_type})"
            )

            return node_data

        except Neo4jError:
            raise

        except Exception as e:

            self.logger.error(
                f"Failed to create/update node "
                f"{node_id}: {e}"
            )

            raise Neo4jError(
                f"Failed to create/update node "
                f"{node_id}: {e}"
            ) from e

    # ============================================================
    # GET NODE
    # ============================================================

    def get_node(
        self,
        node_id: str,
    ) -> Dict[str, Any]:
        """Get a node by ID."""

        if not neo4j.is_connected():

            raise Neo4jError(
                "Neo4j is not connected"
            )

        query = """
        MATCH (n:Node {id: $id})
        RETURN n
        """

        try:

            result = neo4j.execute_query(
                query,
                {
                    "id": node_id,
                },
            )

            if not result:

                raise NodeNotFoundError(
                    f"Node {node_id} not found"
                )

            return result[0].get(
                "n",
                {},
            )

        except NodeNotFoundError:
            raise

        except Exception as e:

            self.logger.error(
                f"Failed to get node "
                f"{node_id}: {e}"
            )

            raise Neo4jError(
                f"Failed to get node "
                f"{node_id}: {e}"
            ) from e

    # ============================================================
    # UPDATE NODE
    # ============================================================

    def update_node(
        self,
        node_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update node properties."""

        if not neo4j.is_connected():

            raise Neo4jError(
                "Neo4j is not connected"
            )

        properties = {
            key: value
            for key, value in properties.items()
            if value is not None
        }

        query = """
        MATCH (n:Node {id: $id})

        SET n += $properties

        SET n.updated_at = $updated_at

        RETURN n
        """

        parameters = {
            "id": node_id,
            "properties": properties,
            "updated_at": (
                datetime.utcnow().isoformat()
                + "Z"
            ),
        }

        try:

            result = neo4j.execute_query(
                query,
                parameters,
            )

            if not result:

                raise NodeNotFoundError(
                    f"Node {node_id} not found"
                )

            self.logger.info(
                f"Updated node: {node_id}"
            )

            return result[0].get(
                "n",
                {},
            )

        except NodeNotFoundError:
            raise

        except Exception as e:

            self.logger.error(
                f"Failed to update node "
                f"{node_id}: {e}"
            )

            raise Neo4jError(
                f"Failed to update node "
                f"{node_id}: {e}"
            ) from e

    # ============================================================
    # DELETE NODE
    # ============================================================

    def delete_node(
        self,
        node_id: str,
    ) -> bool:
        """Delete a node and its relationships."""

        if not neo4j.is_connected():

            raise Neo4jError(
                "Neo4j is not connected"
            )

        query = """
        MATCH (n:Node {id: $id})

        DETACH DELETE n

        RETURN count(n) AS deleted
        """

        try:

            result = neo4j.execute_query(
                query,
                {
                    "id": node_id,
                },
            )

            deleted = (
                result[0].get(
                    "deleted",
                    0,
                )
                if result
                else 0
            )

            if deleted == 0:

                raise NodeNotFoundError(
                    f"Node {node_id} not found"
                )

            self.logger.info(
                f"Deleted node: {node_id}"
            )

            return True

        except NodeNotFoundError:
            raise

        except Exception as e:

            self.logger.error(
                f"Failed to delete node "
                f"{node_id}: {e}"
            )

            raise Neo4jError(
                f"Failed to delete node "
                f"{node_id}: {e}"
            ) from e

    # ============================================================
    # GET ALL NODES
    # ============================================================

    def get_all_nodes(
        self,
        node_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get all nodes."""

        if not neo4j.is_connected():
            return []

        limit = max(
            1,
            min(int(limit), 1000),
        )

        if node_type:

            query = f"""
            MATCH (n:Node)
            WHERE n.type = $type
            RETURN n
            LIMIT {limit}
            """

            parameters = {
                "type": str(node_type).upper(),
            }

        else:

            query = f"""
            MATCH (n:Node)
            RETURN n
            LIMIT {limit}
            """

            parameters = {}

        try:

            result = neo4j.execute_query(
                query,
                parameters,
            )

            return [
                record.get("n", {})
                for record in result
            ]

        except Exception as e:

            self.logger.error(
                f"Failed to get nodes: {e}"
            )

            return []

    # ============================================================
    # GET NODE TYPES
    # ============================================================

    def get_node_types(self) -> List[str]:
        """Get all node types."""

        if not neo4j.is_connected():
            return []

        query = """
        MATCH (n:Node)

        RETURN DISTINCT n.type AS type

        ORDER BY type
        """

        try:

            result = neo4j.execute_query(
                query
            )

            return [
                record.get("type")
                for record in result
                if record.get("type")
            ]

        except Exception as e:

            self.logger.error(
                f"Failed to get node types: {e}"
            )

            return []

    # ============================================================
    # GET NODES BY PROPERTY
    # ============================================================

    def get_nodes_by_property(
        self,
        property_name: str,
        property_value: Any,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get nodes by property.

        Note:
        Neo4j does not allow parameterized property names,
        so property_name must be validated before interpolation.
        """

        if not neo4j.is_connected():
            return []

        allowed_property = (
            str(property_name)
            .strip()
        )

        if not allowed_property:

            raise Neo4jError(
                "Property name cannot be empty"
            )

        # Prevent Cypher injection through property name.
        if not all(
            char.isalnum() or char == "_"
            for char in allowed_property
        ):

            raise Neo4jError(
                "Invalid property name"
            )

        limit = max(
            1,
            min(int(limit), 1000),
        )

        query = f"""
        MATCH (n:Node)

        WHERE n.{allowed_property} = $property_value

        RETURN n

        LIMIT {limit}
        """

        parameters = {
            "property_value": property_value,
        }

        try:

            result = neo4j.execute_query(
                query,
                parameters,
            )

            return [
                record.get("n", {})
                for record in result
            ]

        except Exception as e:

            self.logger.error(
                f"Failed to get nodes by property: {e}"
            )

            return []