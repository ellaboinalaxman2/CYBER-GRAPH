"""
Client for communicating with the Database Engine.

Ingestion Service
        ↓
Database Engine
        ↓
Neo4j
"""

from typing import Dict, Any

import httpx

from src.core.config import settings
from src.core.logging import get_logger


class DatabaseClient:
    """
    HTTP client used by the ingestion service
    to store graph data through the database service.
    """

    def __init__(self):
        self.logger = get_logger("integration.database")

        self.base_url = getattr(
            settings,
            "database_url",
            "http://localhost:8003",
        ).rstrip("/")

        self.timeout = 30.0

    def store_event(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Store a normalized security event in Neo4j
        through the Database Engine.
        """

        url = f"{self.base_url}/api/v1/graph/events"

        self.logger.info(
            f"Sending event {event.get('event_id')} "
            f"to Database Engine: {url}"
        )

        try:
            with httpx.Client(
                timeout=self.timeout
            ) as client:

                response = client.post(
                    url,
                    json=event,
                )

                response.raise_for_status()

                result = response.json()

                if result.get("neo4j") is not True:
                    raise RuntimeError(
                        "Database Engine did not confirm Neo4j storage"
                    )

                self.logger.info(
                    f"Event stored in Neo4j: "
                    f"{event.get('event_id')}"
                )

                return result

        except httpx.ConnectError as e:

            self.logger.error(
                f"Cannot connect to Database Engine "
                f"at {self.base_url}: {e}"
            )

            raise RuntimeError(
                "Database Engine is not running. "
                f"Expected: {self.base_url}"
            )

        except httpx.HTTPStatusError as e:

            self.logger.error(
                f"Database Engine returned "
                f"{e.response.status_code}: "
                f"{e.response.text}"
            )

            raise RuntimeError(
                f"Database Engine error: "
                f"{e.response.text}"
            )

        except Exception as e:

            self.logger.error(
                f"Failed to store event in database: {e}"
            )

            raise