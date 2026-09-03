"""
Event processing worker.
"""

from typing import Dict, Any, Optional

from src.workers.base_worker import BaseWorker
from src.pipeline import Pipeline
from src.core.logging import get_logger
from src.integrations.database_client import DatabaseClient


class EventWorker(BaseWorker):
    """
    Processes events through the ingestion pipeline
    and stores successful events in Neo4j.
    """

    def __init__(self, name: Optional[str] = None):

        super().__init__(
            name=name or "event-worker"
        )

        self.pipeline = Pipeline()

        self.database_client = DatabaseClient()

        self.logger = get_logger(
            "worker.event"
        )

    def process(
        self,
        message: Dict[str, Any],
    ) -> Dict[str, Any]:

        self.logger.info(
            f"Processing event: "
            f"{message.get('event_id', 'unknown')}"
        )

        # ---------------------------------------------------------
        # Extract event
        # ---------------------------------------------------------

        event = message.get(
            "event",
            message,
        )

        # ---------------------------------------------------------
        # Run ingestion pipeline
        # ---------------------------------------------------------

        context = self.pipeline.process_event(
            event
        )

        # ---------------------------------------------------------
        # Check pipeline
        # ---------------------------------------------------------

        if not context.is_successful:

            raise Exception(
                f"Pipeline failed: "
                f"{context.errors}"
            )

        # ---------------------------------------------------------
        # Get normalized/enriched event
        # ---------------------------------------------------------

        processed_event = context.current_data

        if not processed_event:

            raise Exception(
                "Pipeline completed but "
                "no processed event data was returned"
            )

        # ---------------------------------------------------------
        # Store in Neo4j
        # ---------------------------------------------------------

        self.logger.info(
            f"Storing event in Neo4j: "
            f"{processed_event.get('event_id', 'unknown')}"
        )

        graph_result = (
            self.database_client.store_event(
                processed_event
            )
        )

        # ---------------------------------------------------------
        # Return
        # ---------------------------------------------------------

        return {
            "status": "success",

            "event_id": processed_event.get(
                "event_id",
                "unknown",
            ),

            "run_id": context.run_id,

            "processing_time_ms":
                context.processing_time_ms,

            "stage_count":
                len(context.stage_results),

            "neo4j": True,

            "graph": graph_result,
        }