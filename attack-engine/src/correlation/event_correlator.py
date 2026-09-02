"""Event correlator for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

from src.core.logging import get_logger
from src.core.exceptions import CorrelationError
from src.models.event import EventModel
from src.models.incident import IncidentModel
from src.correlation.correlation_rules import CorrelationRules, CorrelationRule


class EventCorrelator:
    """
    Correlates related security events into incidents.
    
    Features:
    - Group related events
    - Time-based correlation
    - Source/destination correlation
    - Event type correlation
    - Correlation rules engine
    """
    
    def __init__(self):
        """Initialize the event correlator."""
        self.logger = get_logger("correlation.event_correlator")
        self.rules = CorrelationRules.get_all_rules()
    
    def correlate(self, events: List[Dict[str, Any]]) -> List[IncidentModel]:
        """
        Correlate events into incidents.
        
        Args:
            events: List of security events
            
        Returns:
            List[IncidentModel]: Correlated incidents
        """
        if not events:
            return []
        
        self.logger.info(f"Correlating {len(events)} events")
        
        # Convert to EventModel if needed
        event_objects = []
        for event in events:
            if isinstance(event, dict):
                event_objects.append(EventModel(**event))
            else:
                event_objects.append(event)
        
        # Track processed events
        processed_event_ids = set()
        incidents = []
        
        # Apply correlation rules
        for rule in self.rules:
            matched_events = self._apply_rule(event_objects, rule)
            
            if matched_events:
                incident = self._create_incident(matched_events, rule)
                incidents.append(incident)
                
                # Mark events as processed
                for event in matched_events:
                    processed_event_ids.add(event.event_id)
        
        # Handle remaining events (time-based correlation)
        remaining_events = [e for e in event_objects if e.event_id not in processed_event_ids]
        if remaining_events:
            time_incidents = self._correlate_by_time(remaining_events)
            incidents.extend(time_incidents)
        
        self.logger.info(f"Created {len(incidents)} incidents from {len(events)} events")
        return incidents
    
    def _apply_rule(self, events: List[EventModel], rule: CorrelationRule) -> List[EventModel]:
        """Apply a correlation rule to events."""
        # Filter events matching rule event types
        matching_events = [e for e in events if e.event_type in rule.event_types]
        
        if len(matching_events) < rule.min_count:
            return []
        
        # Group by source (IP or hostname)
        grouped = defaultdict(list)
        for event in matching_events:
            key = event.source_ip or event.source_hostname or "unknown"
            grouped[key].append(event)
        
        # Find groups that meet the rule criteria
        for source, group_events in grouped.items():
            if len(group_events) >= rule.min_count:
                # Check time window
                timestamps = [e.timestamp for e in group_events]
                if len(timestamps) > 1:
                    time_range = max(timestamps) - min(timestamps)
                    if time_range.total_seconds() <= rule.time_window:
                        return group_events
        
        return []
    
    def _create_incident(self, events: List[EventModel], rule: CorrelationRule) -> IncidentModel:
        """Create an incident from correlated events."""
        event_ids = [e.event_id for e in events]
        timestamps = [e.timestamp for e in events]
        
        # Determine attack type from rule
        attack_type = rule.name.replace("_", " ").title()
        
        # Create incident
        incident = IncidentModel(
            incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
            title=rule.description,
            description=f"{rule.description} ({len(events)} events)",
            severity=rule.severity,
            risk_score=rule.risk_score,
            event_ids=event_ids,
            attack_type=attack_type,
            started_at=min(timestamps),
            detected_at=datetime.utcnow(),
            status="OPEN",
            tags=rule.tags,
        )
        
        self.logger.info(f"Created incident {incident.incident_id}: {rule.description}")
        return incident
    
    def _correlate_by_time(self, events: List[EventModel]) -> List[IncidentModel]:
        """Correlate events by time windows (fallback)."""
        if len(events) < 3:
            return []
        
        incidents = []
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        
        i = 0
        while i < len(sorted_events):
            window_start = sorted_events[i].timestamp
            window_events = [sorted_events[i]]
            j = i + 1
            
            while j < len(sorted_events):
                time_diff = (sorted_events[j].timestamp - window_start).total_seconds()
                if time_diff <= 300:  # 5 minutes window
                    window_events.append(sorted_events[j])
                    j += 1
                else:
                    break
            
            if len(window_events) >= 3:
                # Calculate average anomaly score if available
                scores = [e.anomaly_score for e in window_events if e.anomaly_score is not None]
                avg_score = sum(scores) / len(scores) if scores else 0.3
                
                risk_score = min(50 + (avg_score * 50), 85)
                
                incident = IncidentModel(
                    incident_id=f"INC-TIME-{uuid.uuid4().hex[:6].upper()}",
                    title=f"Activity burst with {len(window_events)} events",
                    description=f"{len(window_events)} events in 5 minutes",
                    severity="MEDIUM" if risk_score > 50 else "LOW",
                    risk_score=risk_score,
                    event_ids=[e.event_id for e in window_events],
                    attack_type="Suspicious Activity Burst",
                    started_at=min(e.timestamp for e in window_events),
                    detected_at=datetime.utcnow(),
                    status="OPEN",
                    tags=["time_correlation", "activity_burst"],
                )
                incidents.append(incident)
            
            i = j
        
        return incidents