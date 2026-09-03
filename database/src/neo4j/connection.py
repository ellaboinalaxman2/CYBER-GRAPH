"""Neo4j connection management."""

from typing import Optional, Dict, Any, List, Tuple

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import Neo4jError


class Neo4jConnection:
    """
    Neo4j connection manager.

    Features:
    - Connection pooling
    - Health checks
    - Session management
    - Query execution
    - Transaction execution
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern."""

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        """Initialize Neo4j connection."""

        if hasattr(self, "_initialized"):
            return

        self.logger = get_logger(
            "neo4j.connection"
        )

        self._initialized = True
        self._connected = False
        self._driver: Optional[Driver] = None

        self._connect()

    # ============================================================
    # CONNECT
    # ============================================================

    def _connect(self) -> None:
        """Connect to Neo4j."""

        try:

            if not hasattr(
                settings,
                "neo4j_uri",
            ):

                self.logger.warning(
                    "Neo4j settings not configured"
                )

                return

            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(
                    settings.neo4j_user,
                    settings.neo4j_password,
                ),
                max_connection_pool_size=50,
                connection_acquisition_timeout=30,
                connection_timeout=30,
            )

            with self._driver.session() as session:

                result = session.run(
                    "RETURN 1 AS test"
                )

                result.single()

            self._connected = True

            self.logger.info(
                f"Connected to Neo4j: "
                f"{settings.neo4j_uri}"
            )

        except (
            ServiceUnavailable,
            AuthError,
        ) as e:

            self._connected = False

            self.logger.error(
                f"Failed to connect to Neo4j: {e}"
            )

        except Exception as e:

            self._connected = False

            self.logger.error(
                f"Unexpected Neo4j error: {e}"
            )

    # ============================================================
    # DRIVER
    # ============================================================

    def get_driver(
        self,
    ) -> Optional[Driver]:
        """Get Neo4j driver."""

        if (
            not self._connected
            or self._driver is None
        ):

            self._connect()

        return self._driver

    # ============================================================
    # SESSION
    # ============================================================

    def get_session(
        self,
    ) -> Optional[Session]:
        """Get a Neo4j session."""

        driver = self.get_driver()

        if driver:
            return driver.session()

        return None

    # ============================================================
    # EXECUTE QUERY
    # ============================================================

    def execute_query(
        self,
        query: str,
        parameters: Optional[
            Dict[str, Any]
        ] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.

        Returns:
            List of dictionaries.
        """

        if (
            not self._connected
            or self._driver is None
        ):

            raise Neo4jError(
                "Neo4j is not connected"
            )

        try:

            with self._driver.session() as session:

                result = session.run(
                    query,
                    parameters or {},
                )

                records = []

                for record in result:

                    records.append(
                        record.data()
                    )

                return records

        except Exception as e:

            self.logger.error(
                f"Query execution failed: {e}"
            )

            raise Neo4jError(
                f"Neo4j query execution failed: {e}"
            ) from e

    # ============================================================
    # TRANSACTION
    # ============================================================

    def execute_transaction(
        self,
        queries: List[
            Tuple[str, Dict[str, Any]]
        ],
    ) -> List[Dict[str, Any]]:
        """Execute multiple queries in a transaction."""

        if (
            not self._connected
            or self._driver is None
        ):

            raise Neo4jError(
                "Neo4j is not connected"
            )

        results = []

        try:

            with self._driver.session() as session:

                with session.begin_transaction() as tx:

                    for query, parameters in queries:

                        result = tx.run(
                            query,
                            parameters or {},
                        )

                        for record in result:

                            results.append(
                                record.data()
                            )

                    tx.commit()

            return results

        except Exception as e:

            self.logger.error(
                f"Transaction execution failed: {e}"
            )

            raise Neo4jError(
                f"Neo4j transaction failed: {e}"
            ) from e

    # ============================================================
    # CONNECTION STATUS
    # ============================================================

    def is_connected(self) -> bool:
        """Check Neo4j connection."""

        if (
            not self._connected
            or self._driver is None
        ):

            return False

        try:

            with self._driver.session() as session:

                result = session.run(
                    "RETURN 1 AS test"
                )

                result.single()

            return True

        except Exception as e:

            self.logger.warning(
                f"Neo4j health check failed: {e}"
            )

            self._connected = False

            return False

    # ============================================================
    # HEALTH CHECK
    # ============================================================

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """Return Neo4j health information."""

        if not self._connected:

            return {
                "status": "unavailable",
                "error": "Neo4j not connected",
            }

        try:

            if not self.is_connected():

                return {
                    "status": "unhealthy",
                    "error": "Connection failed",
                }

            result = self.execute_query(
                """
                MATCH (n:Node)

                RETURN count(n) AS node_count
                """
            )

            node_count = (
                result[0].get(
                    "node_count",
                    0,
                )
                if result
                else 0
            )

            return {
                "status": "healthy",
                "node_count": node_count,
                "uri": getattr(
                    settings,
                    "neo4j_uri",
                    "not configured",
                ),
            }

        except Exception as e:

            return {
                "status": "unhealthy",
                "error": str(e),
            }

    # ============================================================
    # CLOSE
    # ============================================================

    def close(self) -> None:
        """Close Neo4j connection."""

        if self._driver:

            try:

                self._driver.close()

                self._driver = None
                self._connected = False

                self.logger.info(
                    "Neo4j connection closed"
                )

            except Exception as e:

                self.logger.error(
                    f"Error closing Neo4j connection: {e}"
                )


# ================================================================
# SINGLETON
# ================================================================

neo4j = Neo4jConnection()