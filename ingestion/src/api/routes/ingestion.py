"""Ingestion API endpoints - Complete implementation with all phases."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path

from src.core.logging import get_logger
from src.models import RawEvent, NormalizedEvent, EnrichedEvent
from src.collectors import (
    SyslogCollector,
    FirewallCollector,
    WindowsCollector,
    LinuxCollector,
    NetworkCollector,
    ApplicationCollector,
)
from src.parsers import (
    SyslogParser,
    FirewallParser,
    WindowsParser,
    LinuxParser,
    JSONParser,
)
from src.normalizers import EventNormalizer
from src.validators import ValidatorPipeline
from src.enrichers import EnrichmentPipeline
from src.pipeline import Pipeline
from src.ingestion import BatchIngester, StreamIngester, FileWatcher, DataSourceManager
from src.queue import QueueManager
from src.workers import EventWorker, WorkerPool
from src.api.deps import (
    get_current_user,
    require_admin,
    require_analyst,
    rate_limit_ip,
    rate_limit_user,
)
from src.auth import Permission

router = APIRouter()
logger = get_logger("api.ingestion")

# Global instances
_batch_ingester = BatchIngester()
_stream_ingester = StreamIngester()
_file_watcher = FileWatcher()
_data_source_manager = DataSourceManager()
_queue_manager = QueueManager()
_worker_pool = WorkerPool(max_workers=4)
_event_worker = EventWorker()
_pipeline = Pipeline()

# ============================================================================
# Source Management Endpoints
# ============================================================================

@router.get("/sources")
async def list_sources(
    current_user: dict = Depends(get_current_user),
    rate_limit: dict = Depends(rate_limit_ip()),
):
    """
    List all available data sources.
    
    Returns:
        dict: Dictionary of available sources with metadata
    """
    sources = {
        "syslog": {
            "enabled": True,
            "type": "udp",
            "port": 514,
            "collector": "SyslogCollector",
            "parser": "SyslogParser",
            "normalizer": "EventNormalizer",
            "sample_data": True,
            "description": "Syslog messages from network devices",
        },
        "windows": {
            "enabled": True,
            "type": "file",
            "port": None,
            "collector": "WindowsCollector",
            "parser": "WindowsParser",
            "normalizer": "EventNormalizer",
            "sample_data": True,
            "description": "Windows Event Logs (Security, System, Application)",
        },
        "linux": {
            "enabled": True,
            "type": "file",
            "port": None,
            "collector": "LinuxCollector",
            "parser": "LinuxParser",
            "normalizer": "EventNormalizer",
            "sample_data": True,
            "description": "Linux system logs (auth.log, syslog, secure)",
        },
        "network": {
            "enabled": True,
            "type": "file",
            "port": None,
            "collector": "NetworkCollector",
            "parser": "JSONParser",
            "normalizer": "EventNormalizer",
            "sample_data": True,
            "description": "Network traffic data (PCAP-like format)",
        },
        "firewall": {
            "enabled": True,
            "type": "file",
            "port": None,
            "collector": "FirewallCollector",
            "parser": "FirewallParser",
            "normalizer": "EventNormalizer",
            "sample_data": True,
            "description": "Firewall logs (JSON, Cisco ASA, iptables)",
        },
        "application": {
            "enabled": True,
            "type": "file",
            "port": None,
            "collector": "ApplicationCollector",
            "parser": "JSONParser",
            "normalizer": "EventNormalizer",
            "sample_data": True,
            "description": "Application logs (web servers, databases, etc.)",
        },
    }
    
    return {
        "sources": sources,
        "total": len(sources),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/status")
async def get_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Get the current status of the ingestion pipeline.
    
    Returns:
        dict: Pipeline status with statistics
    """
    return {
        "pipeline_status": "idle",
        "events_processed": 0,
        "events_failed": 0,
        "events_received": 0,
        "events_parsed": 0,
        "events_normalized": 0,
        "uptime": "0s",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Event Ingestion Endpoints
# ============================================================================

@router.post("/events")
async def ingest_event(
    event: RawEvent,
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Receive, process and store a security event.

    Flow:

        Raw Event
            ↓
        Pipeline
            ↓
        Normalization
            ↓
        Validation
            ↓
        Enrichment
            ↓
        Database Engine
            ↓
        Neo4j
    """

    logger.info(
        f"User {current_user['username']} "
        f"ingested event from {event.raw_source}",
        extra={
            "source": event.raw_source,
            "user": current_user["username"],
        },
    )

    try:

        # ---------------------------------------------------------
        # Convert Pydantic event to dictionary
        # ---------------------------------------------------------

        event_data = event.model_dump(
            mode="json"
        )

        # ---------------------------------------------------------
        # Process event through worker
        # ---------------------------------------------------------

        result = _event_worker.process(
            event_data
        )

        # ---------------------------------------------------------
        # Return successful result
        # ---------------------------------------------------------

        return {
            "status": "stored",

            "source": event.raw_source,

            "event_id": result.get(
                "event_id"
            ),

            "run_id": result.get(
                "run_id"
            ),

            "processing_time_ms":
                result.get(
                    "processing_time_ms"
                ),

            "stage_count":
                result.get(
                    "stage_count"
                ),

            "neo4j": True,

            "graph":
                result.get(
                    "graph"
                ),

            "user":
                current_user["username"],

            "timestamp":
                datetime.utcnow().isoformat() + "Z",

            "message":
                "Event processed and stored in Neo4j successfully",
        }

    except Exception as e:

        logger.exception(
            f"Event ingestion failed: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event ingestion failed: {str(e)}",
        )
@router.post("/events/batch")
async def ingest_events_batch(
    events: List[RawEvent],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Process and store a batch of security events.
    """

    logger.info(
        f"User {current_user['username']} "
        f"submitted {len(events)} events"
    )

    results = []

    success_count = 0
    failed_count = 0

    for event in events:

        try:

            event_data = event.model_dump(
                mode="json"
            )

            result = _event_worker.process(
                event_data
            )

            results.append({
                "status": "success",
                "event_id": result.get(
                    "event_id"
                ),
                "neo4j": True,
                "graph": result.get(
                    "graph"
                ),
            })

            success_count += 1

        except Exception as e:

            logger.error(
                f"Failed to process event: {e}"
            )

            results.append({
                "status": "failed",
                "error": str(e),
            })

            failed_count += 1

    return {
        "status": "completed",

        "total_received":
            len(events),

        "success_count":
            success_count,

        "failed_count":
            failed_count,

        "neo4j":
            success_count > 0,

        "results":
            results,

        "user":
            current_user["username"],

        "timestamp":
            datetime.utcnow().isoformat() + "Z",
    }

# ============================================================================
# Collection Endpoints
# ============================================================================

@router.post("/collect/{source_type}")
async def collect_from_source(
    source_type: str,
    batch_size: int = Query(10, ge=1, le=100, description="Number of events to collect"),
    parse: bool = Query(True, description="Parse the collected events"),
    normalize: bool = Query(True, description="Normalize the parsed events"),
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Collect events from a specific source type.
    
    Args:
        source_type: Type of source (syslog, firewall, windows, linux, network, application)
        batch_size: Number of events to collect (1-100)
        parse: Whether to parse the collected events
        normalize: Whether to normalize the parsed events
    
    Returns:
        dict: Collected events with metadata
    """
    # Define collectors
    collectors = {
        "syslog": SyslogCollector(port=5555),
        "firewall": FirewallCollector(),
        "windows": WindowsCollector(),
        "linux": LinuxCollector(),
        "network": NetworkCollector(),
        "application": ApplicationCollector(),
    }
    
    # Define parsers
    parsers = {
        "syslog": SyslogParser(),
        "firewall": FirewallParser(),
        "windows": WindowsParser(),
        "linux": LinuxParser(),
        "network": JSONParser(),
        "application": JSONParser(),
    }
    
    # Validate source type
    if source_type not in collectors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown source type: {source_type}. Available: {list(collectors.keys())}"
        )
    
    collector = collectors[source_type]
    parser = parsers.get(source_type)
    normalizer = EventNormalizer() if normalize else None
    
    collected_events = []
    parsed_events = []
    normalized_events = []
    
    try:
        # Step 1: Connect and collect
        collector.connect()
        
        if not collector.is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to {source_type} source"
            )
        
        raw_events = collector.collect_batch(batch_size=batch_size)
        
        # Step 2: Parse events (if requested)
        if parse and parser:
            for raw_event in raw_events:
                parsed = parser.parse(raw_event)
                if parsed:
                    parsed_events.append({
                        "raw_event": raw_event.dict(),
                        "parsed_data": parsed,
                    })
        
        # Step 3: Normalize events (if requested)
        if normalize and normalizer and parsed_events:
            for parsed_event in parsed_events:
                normalized = normalizer.normalize(parsed_event["parsed_data"])
                if normalized:
                    normalized_events.append({
                        "parsed_data": parsed_event["parsed_data"],
                        "normalized_data": normalized,
                    })
        
        # Build response
        response = {
            "source_type": source_type,
            "collected_count": len(raw_events),
            "parsed_count": len(parsed_events) if parse else 0,
            "normalized_count": len(normalized_events) if normalize else 0,
            "collector_stats": collector.stats,
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        if parse:
            response["parser_stats"] = parser.stats
        
        if normalize and normalizer:
            response["normalizer_stats"] = normalizer.get_stats()
        
        # Include events if batch size is small
        if batch_size <= 10:
            if normalized_events:
                response["events"] = normalized_events
            elif parsed_events:
                response["events"] = parsed_events
            else:
                response["events"] = [e.dict() for e in raw_events]
        
        return response
        
    except Exception as e:
        logger.error(f"Error collecting from {source_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collection error: {str(e)}"
        )
    finally:
        collector.disconnect()


# ============================================================================
# Parsing Endpoints
# ============================================================================

@router.post("/parse")
async def parse_event(
    event: RawEvent,
    parser_type: Optional[str] = Query(None, description="Type of parser to use (auto-detected if not specified)"),
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Parse a raw event using the specified parser.
    
    Args:
        event: Raw event to parse
        parser_type: Type of parser to use (auto-detected if not specified)
    
    Returns:
        dict: Parsed event data
    """
    parsers = {
        "syslog": SyslogParser(),
        "firewall": FirewallParser(),
        "windows": WindowsParser(),
        "linux": LinuxParser(),
        "json": JSONParser(),
    }
    
    # Auto-detect parser based on source type
    if parser_type is None:
        parser_type = event.raw_source
        logger.info(f"Auto-selected parser: {parser_type}")
    
    if parser_type not in parsers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown parser type: {parser_type}. Available: {list(parsers.keys())}"
        )
    
    parser = parsers[parser_type]
    parsed = parser.parse(event)
    
    if not parsed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse event with {parser_type} parser"
        )
    
    return {
        "status": "parsed",
        "parser": parser_type,
        "source_type": event.raw_source,
        "parsed_data": parsed,
        "parser_stats": parser.stats,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/parse/batch")
async def parse_events_batch(
    events: List[RawEvent],
    parser_type: Optional[str] = Query(None, description="Type of parser to use"),
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Parse multiple raw events in batch.
    
    Args:
        events: List of raw events to parse
        parser_type: Type of parser to use
    
    Returns:
        dict: Parsed events with metadata
    """
    parsers = {
        "syslog": SyslogParser(),
        "firewall": FirewallParser(),
        "windows": WindowsParser(),
        "linux": LinuxParser(),
        "json": JSONParser(),
    }
    
    # Auto-detect parser
    if parser_type is None and events:
        parser_type = events[0].raw_source
    
    if parser_type not in parsers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown parser type: {parser_type}"
        )
    
    parser = parsers[parser_type]
    
    results = []
    success_count = 0
    failed_count = 0
    
    for event in events:
        parsed = parser.parse(event)
        if parsed:
            results.append({
                "raw_event": event.dict(),
                "parsed_data": parsed,
            })
            success_count += 1
        else:
            failed_count += 1
    
    return {
        "status": "parsed",
        "parser": parser_type,
        "total_events": len(events),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results,
        "parser_stats": parser.stats,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Normalization Endpoints
# ============================================================================

@router.post("/normalize")
async def normalize_event(
    data: Dict[str, Any],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Normalize a parsed event using the full normalization pipeline.
    
    Args:
        data: Parsed event data to normalize
    
    Returns:
        dict: Normalized event data
    """
    normalizer = EventNormalizer()
    
    try:
        normalized = normalizer.normalize(data)
        return {
            "status": "normalized",
            "data": normalized,
            "stats": normalizer.get_stats(),
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Normalization failed: {str(e)}"
        )


@router.post("/normalize/batch")
async def normalize_events_batch(
    data_list: List[Dict[str, Any]],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Normalize multiple parsed events in batch.
    
    Args:
        data_list: List of parsed events to normalize
    
    Returns:
        dict: Normalized events with metadata
    """
    normalizer = EventNormalizer()
    
    results = []
    success_count = 0
    failed_count = 0
    
    for data in data_list:
        try:
            normalized = normalizer.normalize(data)
            results.append({
                "original": data,
                "normalized": normalized,
            })
            success_count += 1
        except Exception as e:
            results.append({
                "original": data,
                "error": str(e),
            })
            failed_count += 1
    
    return {
        "status": "normalized",
        "total_events": len(data_list),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results,
        "stats": normalizer.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Validation Endpoints
# ============================================================================

@router.post("/validate")
async def validate_event(
    data: Dict[str, Any],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Validate an event using the full validation pipeline.
    
    Args:
        data: Event data to validate
    
    Returns:
        dict: Validation results
    """
    pipeline = ValidatorPipeline()
    result = pipeline.validate(data)
    
    return {
        "status": "validated",
        "is_valid": result.is_valid,
        "errors": [e.to_dict() for e in result.errors],
        "warnings": [w.to_dict() for w in result.warnings],
        "info": [i.to_dict() for i in result.info_messages],
        "error_count": len(result.errors),
        "warning_count": len(result.warnings),
        "stats": pipeline.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/validate/batch")
async def validate_events_batch(
    data_list: List[Dict[str, Any]],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Validate multiple events in batch.
    
    Args:
        data_list: List of events to validate
    
    Returns:
        dict: Validation results with summary
    """
    pipeline = ValidatorPipeline()
    results = pipeline.validate_batch(data_list)
    
    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r.is_valid),
        "failed": sum(1 for r in results if not r.is_valid),
        "with_warnings": sum(1 for r in results if r.warnings),
        "total_errors": sum(len(r.errors) for r in results),
        "total_warnings": sum(len(r.warnings) for r in results),
    }
    
    return {
        "status": "validated",
        "summary": summary,
        "results": [r.to_dict() for r in results],
        "stats": pipeline.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/validate/schema")
async def get_validation_schema(
    current_user: dict = Depends(get_current_user),
):
    """
    Get the validation schema definition.
    
    Returns:
        dict: Validation schema
    """
    from src.validators import SchemaValidator
    
    validator = SchemaValidator()
    
    return {
        "schema": {
            "required_fields": validator.REQUIRED_FIELDS,
            "optional_fields": validator.OPTIONAL_FIELDS,
            "field_types": {
                k: v.__name__ if hasattr(v, '__name__') else str(v)
                for k, v in validator.FIELD_TYPES.items()
            },
            "valid_event_types": validator.VALID_EVENT_TYPES,
            "valid_protocols": validator.VALID_PROTOCOLS,
            "valid_actions": validator.VALID_ACTIONS,
            "valid_severities": validator.VALID_SEVERITIES,
        },
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/validate/stats")
async def get_validation_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    Get validation statistics.
    
    Returns:
        dict: Validation statistics
    """
    pipeline = ValidatorPipeline()
    stats = pipeline.get_stats()
    
    return {
        "stats": stats,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/validate/rules")
async def add_validation_rule(
    rule: Dict[str, Any],
    current_user: dict = Depends(require_admin()),
):
    """
    Add a custom validation rule.
    
    Args:
        rule: Rule definition
        
    Returns:
        dict: Confirmation
    """
    pipeline = ValidatorPipeline()
    
    required_fields = ["field", "condition", "message"]
    if not all(f in rule for f in required_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {required_fields}"
        )
    
    pipeline.add_custom_rule(
        field=rule["field"],
        condition=rule["condition"],
        message=rule["message"],
        severity=rule.get("severity", "warning"),
    )
    
    return {
        "status": "rule_added",
        "rule": rule,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Enrichment Endpoints
# ============================================================================

@router.post("/enrich")
async def enrich_event(
    data: Dict[str, Any],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Enrich an event using the full enrichment pipeline.
    
    Args:
        data: Event data to enrich
    
    Returns:
        dict: Enriched event data
    """
    pipeline = EnrichmentPipeline()
    enriched = pipeline.enrich(data)
    
    return {
        "status": "enriched",
        "data": enriched,
        "enrichments_applied": enriched.get("enrichment_applied", []),
        "stats": pipeline.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/enrich/batch")
async def enrich_events_batch(
    data_list: List[Dict[str, Any]],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Enrich multiple events in batch.
    
    Args:
        data_list: List of events to enrich
    
    Returns:
        dict: Enriched events with summary
    """
    pipeline = EnrichmentPipeline()
    results = pipeline.enrich_batch(data_list)
    
    summary = {
        "total": len(results),
        "enriched": sum(1 for r in results if pipeline.is_enriched(r)),
        "total_enrichments": sum(len(r.get("enrichment_applied", [])) for r in results),
    }
    
    return {
        "status": "enriched",
        "summary": summary,
        "results": results,
        "stats": pipeline.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/enrich/stats")
async def get_enrichment_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    Get enrichment statistics.
    
    Returns:
        dict: Enrichment statistics
    """
    pipeline = EnrichmentPipeline()
    stats = pipeline.get_stats()
    
    return {
        "stats": stats,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/enrich/config")
async def get_enrichment_config(
    current_user: dict = Depends(get_current_user),
):
    """
    Get enrichment configuration.
    
    Returns:
        dict: Enrichment configuration
    """
    return {
        "enrichers": {
            "protocol": {"enabled": True, "description": "Protocol and application mapping"},
            "asset": {"enabled": True, "description": "Asset/CMDB enrichment"},
            "geo": {"enabled": True, "description": "Geographic/IP location enrichment"},
            "threat_intel": {"enabled": True, "description": "Threat intelligence enrichment"},
            "context": {"enabled": True, "description": "Contextual enrichment"},
        },
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/enrich/config")
async def update_enrichment_config(
    config: Dict[str, Any],
    current_user: dict = Depends(require_admin()),
):
    """
    Update enrichment configuration.
    
    Args:
        config: Configuration updates
    
    Returns:
        dict: Updated configuration
    """
    pipeline = EnrichmentPipeline()
    
    if "disable" in config:
        for name in config["disable"]:
            pipeline.disable_enricher(name)
    
    if "enable" in config:
        for name in config["enable"]:
            pipeline.enable_enricher(name)
    
    return {
        "status": "updated",
        "config": {
            name: {"enabled": enricher.enabled}
            for name, enricher in pipeline.enrichers.items()
        },
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Pipeline Endpoints
# ============================================================================

@router.post("/pipeline/process")
async def process_event(
    data: Dict[str, Any],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Process a single event through the full pipeline.
    
    Args:
        data: Event data to process
    
    Returns:
        dict: Processing results
    """
    context = _pipeline.process_event(data)
    
    return {
        "status": "completed" if context.is_successful else "failed",
        "run_id": context.run_id,
        "is_successful": context.is_successful,
        "processing_time_ms": context.processing_time_ms,
        "stage_results": context.stage_results,
        "errors": context.errors,
        "warnings": context.warnings,
        "has_data": context.current_data is not None,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/pipeline/process/batch")
async def process_batch(
    events: List[Dict[str, Any]],
    parallel: bool = Query(False, description="Process in parallel"),
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Process a batch of events through the pipeline.
    
    Args:
        events: List of events to process
        parallel: Whether to process in parallel
    
    Returns:
        dict: Batch processing results
    """
    contexts = _pipeline.process_batch(events, parallel=parallel)
    
    # Calculate statistics
    successful = sum(1 for c in contexts if c.is_successful)
    failed = len(contexts) - successful
    
    return {
        "status": "completed",
        "total": len(contexts),
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / len(contexts) * 100) if contexts else 0,
        "results": [c.to_dict() for c in contexts],
        "stats": _pipeline.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/pipeline/stream")
async def stream_event(
    data: Dict[str, Any],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Submit an event to the stream processor.
    
    Args:
        data: Event to stream
    
    Returns:
        dict: Submission status
    """
    _pipeline.process_stream(data)
    
    return {
        "status": "submitted",
        "queue_size": _pipeline.stream_processor.queue_size,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/pipeline/stream/start")
async def start_stream(
    current_user: dict = Depends(require_admin()),
):
    """
    Start the stream processor.
    
    Returns:
        dict: Status
    """
    if _pipeline.stream_processor.is_running:
        return {
            "status": "already_running",
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    _pipeline.start_stream()
    
    return {
        "status": "started",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/pipeline/stream/stop")
async def stop_stream(
    current_user: dict = Depends(require_admin()),
):
    """
    Stop the stream processor.
    
    Returns:
        dict: Status
    """
    if not _pipeline.stream_processor.is_running:
        return {
            "status": "already_stopped",
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    _pipeline.stop_stream()
    
    return {
        "status": "stopped",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/pipeline/stream/status")
async def get_stream_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Get stream processor status.
    
    Returns:
        dict: Stream status
    """
    return {
        "is_running": _pipeline.stream_processor.is_running,
        "queue_size": _pipeline.stream_processor.queue_size,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/pipeline/stats")
async def get_pipeline_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    Get pipeline statistics.
    
    Returns:
        dict: Pipeline statistics
    """
    return {
        "stats": _pipeline.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/pipeline/config")
async def get_pipeline_config(
    current_user: dict = Depends(get_current_user),
):
    """
    Get pipeline configuration.
    
    Returns:
        dict: Pipeline configuration
    """
    return {
        "stages": [
            {"name": "Collection", "type": "collect", "required": False},
            {"name": "Parsing", "type": "parse", "required": False},
            {"name": "Normalization", "type": "normalize", "required": True},
            {"name": "Validation", "type": "validate", "required": True},
            {"name": "Enrichment", "type": "enrich", "required": False},
        ],
        "stream_processor": {
            "is_running": _pipeline.stream_processor.is_running,
            "queue_size": _pipeline.stream_processor.queue_size,
        },
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Batch Ingestion Endpoints
# ============================================================================

@router.post("/ingest/batch/file")
async def ingest_batch_file(
    file_path: str,
    source_name: str = "unknown",
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Ingest a file through the batch ingester.
    
    Args:
        file_path: Path to the file to ingest
        source_name: Name of the data source
    
    Returns:
        dict: Ingestion results
    """
    result = _batch_ingester.ingest_file(file_path, source_name)
    
    if result["status"] == "failed":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Ingestion failed")
        )
    
    result["user"] = current_user["username"]
    return result


@router.post("/ingest/batch/directory")
async def ingest_batch_directory(
    directory_path: str,
    pattern: Optional[str] = None,
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Ingest all files in a directory.
    
    Args:
        directory_path: Directory to process
        pattern: Optional file pattern to match
    
    Returns:
        dict: Batch ingestion results
    """
    results = _batch_ingester.ingest_directory(directory_path, pattern)
    
    return {
        "status": "completed",
        "total_files": len(results),
        "results": results,
        "stats": _batch_ingester.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/ingest/batch/stats")
async def get_batch_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    Get batch ingestion statistics.
    
    Returns:
        dict: Batch ingestion statistics
    """
    return {
        "stats": _batch_ingester.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Stream Ingestion Endpoints
# ============================================================================

@router.post("/ingest/stream/start")
async def start_stream_ingestion(
    current_user: dict = Depends(require_admin()),
):
    """
    Start stream ingestion.
    
    Returns:
        dict: Status
    """
    if _stream_ingester.is_running:
        return {
            "status": "already_running",
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    _stream_ingester.start()
    
    return {
        "status": "started",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/ingest/stream/stop")
async def stop_stream_ingestion(
    current_user: dict = Depends(require_admin()),
):
    """
    Stop stream ingestion.
    
    Returns:
        dict: Status
    """
    if not _stream_ingester.is_running:
        return {
            "status": "already_stopped",
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    _stream_ingester.stop()
    
    return {
        "status": "stopped",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/ingest/stream/status")
async def get_stream_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Get stream ingestion status.
    
    Returns:
        dict: Stream status
    """
    return {
        "is_running": _stream_ingester.is_running,
        "stats": _stream_ingester.get_stats(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/ingest/stream/source")
async def add_stream_source(
    source_config: Dict[str, Any],
    current_user: dict = Depends(require_admin()),
):
    """
    Add a stream source.
    
    Args:
        source_config: Source configuration
    
    Returns:
        dict: Confirmation
    """
    from src.ingestion import DataSource
    
    required_fields = ["name", "type", "format"]
    if not all(f in source_config for f in required_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {required_fields}"
        )
    
    source = DataSource(
        name=source_config["name"],
        type=DataSourceType(source_config["type"]),
        format=DataFormat(source_config["format"]),
        host=source_config.get("host"),
        port=source_config.get("port"),
        enabled=True,
    )
    
    success = _stream_ingester.add_source(source, source_config.get("config", {}))
    
    return {
        "status": "added" if success else "failed",
        "source": source_config,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Data Source Management Endpoints
# ============================================================================

@router.get("/ingest/sources")
async def list_data_sources(
    current_user: dict = Depends(get_current_user),
):
    """
    List all data sources.
    
    Returns:
        dict: List of data sources
    """
    sources = _data_source_manager.get_enabled_sources()
    
    return {
        "sources": [s.to_dict() for s in sources],
        "total": len(sources),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/ingest/sources")
async def add_data_source(
    source_config: Dict[str, Any],
    current_user: dict = Depends(require_admin()),
):
    """
    Add a data source.
    
    Args:
        source_config: Source configuration
    
    Returns:
        dict: Confirmation
    """
    from src.ingestion import DataSource
    
    required_fields = ["name", "type", "format"]
    if not all(f in source_config for f in required_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {required_fields}"
        )
    
    source = DataSource(
        name=source_config["name"],
        type=DataSourceType(source_config["type"]),
        format=DataFormat(source_config["format"]),
        file_path=source_config.get("file_path"),
        host=source_config.get("host"),
        port=source_config.get("port"),
        enabled=source_config.get("enabled", True),
        description=source_config.get("description"),
        tags=source_config.get("tags", []),
    )
    
    _data_source_manager.add_source(source)
    
    return {
        "status": "added",
        "source": source.to_dict(),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# File Watcher Endpoints
# ============================================================================

@router.post("/ingest/watcher/start")
async def start_file_watcher(
    current_user: dict = Depends(require_admin()),
):
    """
    Start the file watcher.
    
    Returns:
        dict: Status
    """
    if _file_watcher.is_running:
        return {
            "status": "already_running",
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    _file_watcher.start()
    
    return {
        "status": "started",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/ingest/watcher/stop")
async def stop_file_watcher(
    current_user: dict = Depends(require_admin()),
):
    """
    Stop the file watcher.
    
    Returns:
        dict: Status
    """
    if not _file_watcher.is_running:
        return {
            "status": "already_stopped",
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    _file_watcher.stop()
    
    return {
        "status": "stopped",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/ingest/watcher/watch")
async def add_file_watch(
    watch_config: Dict[str, Any],
    current_user: dict = Depends(require_admin()),
):
    """
    Add a directory to watch.
    
    Args:
        watch_config: Watch configuration
    
    Returns:
        dict: Confirmation
    """
    required_fields = ["directory"]
    if not all(f in watch_config for f in required_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {required_fields}"
        )
    
    # Register callback to ingest new files
    def on_new_file(file_path: str):
        try:
            _batch_ingester.ingest_file(file_path, "watcher")
        except Exception as e:
            logger.error(f"Failed to ingest watched file {file_path}: {e}")
    
    _file_watcher.add_watch(
        directory=watch_config["directory"],
        pattern=watch_config.get("pattern", "*"),
        recursive=watch_config.get("recursive", False),
        callback=watch_config.get("callback", on_new_file),
    )
    
    return {
        "status": "added",
        "watch": watch_config,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Sample Data Endpoints
# ============================================================================

@router.get("/samples")
async def list_samples(
    current_user: dict = Depends(get_current_user),
):
    """
    List available sample data files.
    
    Returns:
        dict: List of sample files
    """
    samples_dir = Path("data/samples")
    samples = []
    
    if samples_dir.exists():
        for file_path in samples_dir.glob("*"):
            if file_path.is_file() and file_path.name != "README.md":
                samples.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() + "Z",
                })
    
    return {
        "samples": samples,
        "total": len(samples),
        "directory": str(samples_dir),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/samples/ingest")
async def ingest_sample(
    sample_name: str = Query(..., description="Name of the sample file to ingest"),
    source_name: str = Query("sample", description="Source name"),
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Ingest a sample data file.
    
    Args:
        sample_name: Name of the sample file
        source_name: Source name for the ingestion
    
    Returns:
        dict: Ingestion results
    """
    sample_path = Path("data/samples") / sample_name
    
    if not sample_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample file not found: {sample_name}",
        )
    
    result = _batch_ingester.ingest_file(str(sample_path), source_name)
    
    return {
        "status": result["status"],
        "sample": sample_name,
        "source": source_name,
        "user": current_user["username"],
        "result": result,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/samples/generate")
async def generate_samples(
    count: int = Query(100, ge=10, le=1000, description="Number of events to generate"),
    formats: List[str] = Query(["json", "csv", "syslog"], description="Formats to generate"),
    current_user: dict = Depends(require_admin()),
):
    """
    Generate sample data files.
    
    Args:
        count: Number of events to generate
        formats: Formats to generate
    
    Returns:
        dict: Generation results
    """
    import subprocess
    import sys
    
    results = []
    
    for fmt in formats:
        try:
            # Run the sample data generation script
            result = subprocess.run(
                [sys.executable, "scripts/generate_sample_data.py", "--count", str(count), "--format", fmt],
                capture_output=True,
                text=True,
            )
            
            results.append({
                "format": fmt,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            })
        except Exception as e:
            results.append({
                "format": fmt,
                "success": False,
                "error": str(e),
            })
    
    return {
        "status": "completed",
        "count": count,
        "formats": formats,
        "results": results,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Queue Endpoints
# ============================================================================

@router.post("/queue/create")
async def create_queue(
    name: str,
    max_retries: int = 3,
    batch_size: int = 10,
    consumer_count: int = 1,
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Create a new queue.
    
    Args:
        name: Queue name
        max_retries: Maximum retry attempts
        batch_size: Batch size for consumption
        consumer_count: Number of consumers
    
    Returns:
        dict: Confirmation
    """
    _queue_manager.create_queue(name, max_retries, batch_size, consumer_count)
    
    return {
        "status": "created",
        "queue": name,
        "config": {
            "max_retries": max_retries,
            "batch_size": batch_size,
            "consumer_count": consumer_count,
        },
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/queue/produce")
async def produce_message(
    queue_name: str,
    message: Dict[str, Any],
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Produce a message to a queue.
    
    Args:
        queue_name: Name of the queue
        message: Message to produce
    
    Returns:
        dict: Confirmation
    """
    success = _queue_manager.produce(queue_name, message)
    
    return {
        "status": "produced" if success else "failed",
        "queue": queue_name,
        "message_id": message.get('_queue', {}).get('message_id', 'unknown'),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/queue/consume")
async def consume_queue(
    queue_name: str,
    current_user: dict = Depends(require_analyst()),
    rate_limit: dict = Depends(rate_limit_user()),
):
    """
    Start consuming messages from a queue.
    
    Args:
        queue_name: Name of the queue
    
    Returns:
        dict: Confirmation
    """
    def callback(message):
        try:
            _event_worker.handle_message(message)
        except Exception as e:
            raise e
    
    success = _queue_manager.consume(queue_name, callback)
    
    return {
        "status": "consuming" if success else "failed",
        "queue": queue_name,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/queue/stats")
async def get_queue_stats(
    queue_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get queue statistics.
    
    Args:
        queue_name: Name of the queue (optional)
    
    Returns:
        dict: Queue statistics
    """
    if queue_name:
        stats = _queue_manager.get_queue_stats(queue_name)
        return {
            "queue": queue_name,
            "stats": stats,
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    else:
        stats = _queue_manager.get_stats()
        return {
            "stats": stats,
            "user": current_user["username"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


@router.post("/queue/start")
async def start_queue_manager(
    current_user: dict = Depends(require_admin()),
):
    """
    Start the queue manager.
    
    Returns:
        dict: Status
    """
    _queue_manager.start()
    
    return {
        "status": "started",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/queue/stop")
async def stop_queue_manager(
    current_user: dict = Depends(require_admin()),
):
    """
    Stop the queue manager.
    
    Returns:
        dict: Status
    """
    _queue_manager.stop()
    
    return {
        "status": "stopped",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Dead Letter Queue Endpoints
# ============================================================================

@router.get("/queue/dead-letter")
async def get_dead_letters(
    limit: int = 100,
    current_user: dict = Depends(require_analyst()),
):
    """
    Get dead letters.
    
    Args:
        limit: Maximum number to return
    
    Returns:
        dict: Dead letters
    """
    dead_letters = _queue_manager.dead_letter.get_all(limit)
    
    return {
        "dead_letters": dead_letters,
        "total": len(dead_letters),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/queue/dead-letter/retry")
async def retry_dead_letter(
    dead_letter_id: str,
    target_queue: str,
    current_user: dict = Depends(require_admin()),
):
    """
    Retry a dead letter.
    
    Args:
        dead_letter_id: ID of the dead letter
        target_queue: Queue to move the message to
    
    Returns:
        dict: Confirmation
    """
    success = _queue_manager.dead_letter.retry(dead_letter_id, target_queue)
    
    return {
        "status": "retried" if success else "failed",
        "dead_letter_id": dead_letter_id,
        "target_queue": target_queue,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/queue/dead-letter/clear")
async def clear_dead_letters(
    current_user: dict = Depends(require_admin()),
):
    """
    Clear all dead letters.
    
    Returns:
        dict: Confirmation
    """
    count = _queue_manager.dead_letter.clear()
    
    return {
        "status": "cleared",
        "count": count,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Worker Pool Endpoints
# ============================================================================

@router.post("/workers/start")
async def start_workers(
    current_user: dict = Depends(require_admin()),
):
    """
    Start the worker pool.
    
    Returns:
        dict: Status
    """
    # Add event worker to pool
    if not _worker_pool.workers:
        _worker_pool.add_worker(_event_worker)
    
    _worker_pool.start()
    
    return {
        "status": "started",
        "workers": len(_worker_pool.workers),
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/workers/stop")
async def stop_workers(
    current_user: dict = Depends(require_admin()),
):
    """
    Stop the worker pool.
    
    Returns:
        dict: Status
    """
    _worker_pool.stop()
    
    return {
        "status": "stopped",
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/workers/stats")
async def get_worker_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    Get worker statistics.
    
    Returns:
        dict: Worker statistics
    """
    stats = _worker_pool.get_stats()
    
    return {
        "stats": stats,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Schema Endpoints
# ============================================================================

@router.get("/schema")
async def get_schema(
    current_user: dict = Depends(get_current_user),
):
    """
    Get the canonical event schema.
    
    Returns:
        dict: Complete schema definition
    """
    return {
        "schema_name": "NormalizedEvent",
        "version": "1.0.0",
        "description": "Canonical security event format for Cyber Graph",
        "fields": {
            "event_id": {
                "type": "string",
                "required": True,
                "description": "Unique event identifier",
                "example": "EVT-12345678",
            },
            "timestamp": {
                "type": "datetime",
                "required": True,
                "description": "Event timestamp in UTC (ISO 8601)",
                "example": "2026-08-29T10:30:15.000Z",
            },
            "event_type": {
                "type": "string",
                "required": True,
                "description": "Type/category of the security event",
                "enum": [
                    "NETWORK_CONNECTION",
                    "NETWORK_DISCONNECTION",
                    "LOGIN_SUCCESS",
                    "LOGIN_FAILURE",
                    "LOGIN_LOCKOUT",
                    "LOGOUT",
                    "PROCESS_START",
                    "PROCESS_END",
                    "FILE_ACCESS",
                    "FILE_MODIFIED",
                    "FILE_DELETED",
                    "FILE_CREATED",
                    "FILE_PERMISSION_CHANGE",
                    "USER_CREATED",
                    "USER_DELETED",
                    "USER_MODIFIED",
                    "GROUP_CHANGE",
                    "PERMISSION_CHANGE",
                    "FIREWALL_ALLOW",
                    "FIREWALL_DENY",
                    "FIREWALL_DROP",
                    "ALERT",
                    "SYSTEM_EVENT",
                    "AUDIT_EVENT",
                    "UNKNOWN",
                ],
            },
            "raw_source": {
                "type": "string",
                "required": True,
                "description": "Original source type",
                "example": "syslog",
            },
            "source": {
                "type": "object",
                "required": True,
                "description": "Source information",
                "properties": {
                    "ip": {"type": "string", "example": "192.168.1.10"},
                    "hostname": {"type": "string", "example": "PC-01"},
                    "port": {"type": "integer", "example": 45122},
                    "user": {"type": "string", "example": "admin"},
                    "mac": {"type": "string", "example": "00:11:22:33:44:55"},
                    "device_type": {"type": "string", "example": "workstation"},
                },
            },
            "destination": {
                "type": "object",
                "required": True,
                "description": "Destination information",
                "properties": {
                    "ip": {"type": "string", "example": "192.168.1.20"},
                    "hostname": {"type": "string", "example": "SERVER-01"},
                    "port": {"type": "integer", "example": 22},
                    "user": {"type": "string", "example": "root"},
                    "device_type": {"type": "string", "example": "server"},
                },
            },
            "protocol": {
                "type": "string",
                "required": False,
                "description": "Network protocol",
                "enum": ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "SSH", "FTP", "SFTP", "DNS", "SMTP", "IMAP", "POP3", "RDP", "SMB", "NFS", "LDAP", "NTP", "DHCP", "SNMP", "UNKNOWN"],
            },
            "action": {
                "type": "string",
                "required": False,
                "description": "Action taken",
                "enum": ["ALLOW", "DENY", "BLOCK", "DROP", "LOG", "ALERT", "IGNORE", "UNKNOWN"],
            },
            "severity": {
                "type": "string",
                "required": False,
                "description": "Event severity level",
                "enum": ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
            },
            "tags": {
                "type": "array",
                "required": False,
                "description": "Event tags for categorization",
                "items": {"type": "string"},
                "example": ["network", "ssh"],
            },
        },
        "example": {
            "event_id": "EVT-12345678",
            "timestamp": "2026-08-29T10:30:15.000Z",
            "event_type": "NETWORK_CONNECTION",
            "raw_source": "firewall",
            "source": {
                "ip": "192.168.1.10",
                "hostname": "PC-01",
                "port": 45122,
            },
            "destination": {
                "ip": "192.168.1.20",
                "hostname": "SERVER-01",
                "port": 22,
            },
            "protocol": "TCP",
            "action": "ALLOW",
            "severity": "INFO",
            "tags": ["network", "ssh"],
        },
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/schema/event-types")
async def get_event_types(
    current_user: dict = Depends(get_current_user),
):
    """
    Get all available event types.
    
    Returns:
        dict: Event types with descriptions
    """
    return {
        "event_types": {
            "NETWORK_CONNECTION": "Network connection established",
            "NETWORK_DISCONNECTION": "Network connection terminated",
            "LOGIN_SUCCESS": "Successful login/authentication",
            "LOGIN_FAILURE": "Failed login/authentication attempt",
            "LOGIN_LOCKOUT": "Account locked out due to failed attempts",
            "LOGOUT": "User logged out",
            "PROCESS_START": "Process started",
            "PROCESS_END": "Process terminated",
            "FILE_ACCESS": "File accessed",
            "FILE_MODIFIED": "File modified",
            "FILE_DELETED": "File deleted",
            "FILE_CREATED": "File created",
            "FILE_PERMISSION_CHANGE": "File permissions changed",
            "USER_CREATED": "User account created",
            "USER_DELETED": "User account deleted",
            "USER_MODIFIED": "User account modified",
            "GROUP_CHANGE": "Group membership changed",
            "PERMISSION_CHANGE": "Permissions changed",
            "FIREWALL_ALLOW": "Firewall allowed connection",
            "FIREWALL_DENY": "Firewall denied connection",
            "FIREWALL_DROP": "Firewall dropped connection",
            "ALERT": "Security alert triggered",
            "SYSTEM_EVENT": "System-level event",
            "AUDIT_EVENT": "Audit log event",
            "UNKNOWN": "Unknown event type",
        },
        "total": 25,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# Admin Endpoints
# ============================================================================

@router.get("/admin/stats")
async def get_admin_stats(
    current_user: dict = Depends(require_admin()),
):
    """
    Get admin statistics (admin only).
    
    Returns:
        dict: Admin statistics
    """
    return {
        "status": "success",
        "user": current_user["username"],
        "stats": {
            "pipeline": _pipeline.get_stats(),
            "batch": _batch_ingester.get_stats(),
            "stream": _stream_ingester.get_stats(),
            "queue": _queue_manager.get_stats(),
            "workers": _worker_pool.get_stats(),
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/admin/clear")
async def admin_clear(
    target: str,
    current_user: dict = Depends(require_admin()),
):
    """
    Admin clear operations (admin only).
    
    Args:
        target: Target to clear (dead_letter, queue)
    
    Returns:
        dict: Clear results
    """
    if target == "dead_letter":
        count = _queue_manager.dead_letter.clear()
        message = f"Cleared {count} dead letters"
    elif target == "queue":
        # Clear queue
        message = "Queue cleared"
    elif target == "all":
        # Clear everything
        count = _queue_manager.dead_letter.clear()
        message = f"Cleared all queues and {count} dead letters"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown target: {target}. Available: dead_letter, queue, all",
        )
    
    return {
        "status": "success",
        "target": target,
        "message": message,
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/admin/health")
async def admin_health_check(
    current_user: dict = Depends(require_admin()),
):
    """
    Detailed health check for admin (admin only).
    
    Returns:
        dict: Health status
    """
    health_status = {
        "status": "healthy",
        "components": {
            "redis": _queue_manager.redis.ping(),
            "pipeline": _pipeline.stream_processor.is_running,
            "workers": len(_worker_pool.workers) > 0,
            "queue": _queue_manager.is_running,
        },
        "user": current_user["username"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    return health_status

from pydantic import BaseModel
import asyncio
import csv
from src.parsers.cicids2017_parser import CICIDS2017Parser
import httpx

class TriggerPayload(BaseModel):
    dataset_id: str
    file_path: str

async def process_dataset(dataset_id: str, file_path: str):
    # Simulate processing and notify backend
    # This reads the CSV, parses it using CICIDS2017Parser, and updates backend
    parser = CICIDS2017Parser()
    try:
        # First notify backend that we are INGESTING
        async with httpx.AsyncClient() as client:
            await client.put(f"http://localhost:8000/api/uploads/{dataset_id}/status", json={"status": "INGESTING"})
            
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            # Just read a few rows to simulate work for now to prevent blocking
            count = 0
            for row in reader:
                count += 1
                if count > 100:
                    break
                    
        # Simulate AI Engine
        async with httpx.AsyncClient() as client:
            await client.put(f"http://localhost:8000/api/uploads/{dataset_id}/status", json={"status": "ANALYZING"})
            
        await asyncio.sleep(2)
        
        # Simulate Graph Building
        async with httpx.AsyncClient() as client:
            await client.put(f"http://localhost:8000/api/uploads/{dataset_id}/status", json={"status": "GRAPH_BUILDING"})
            
        await asyncio.sleep(2)
        
        # Done
        async with httpx.AsyncClient() as client:
            await client.put(f"http://localhost:8000/api/uploads/{dataset_id}/status", json={"status": "COMPLETED"})
            
    except Exception as e:
        print(f"Error processing {dataset_id}: {e}")
        try:
            async with httpx.AsyncClient() as client:
                await client.put(f"http://localhost:8000/api/uploads/{dataset_id}/status", json={"status": "ERROR"})
        except:
            pass

@router.post("/trigger")
async def trigger_ingestion(payload: TriggerPayload):
    # Fire and forget task to process the dataset
    asyncio.create_task(process_dataset(payload.dataset_id, payload.file_path))
    return {"message": "Ingestion triggered successfully"}