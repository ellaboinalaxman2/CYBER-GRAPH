"""Sequence analyzer for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from src.core.logging import get_logger
from src.core.exceptions import ReconstructionError
from src.models.event import EventModel


class SequenceAnalyzer:
    """
    Analyzes event sequences for attack patterns.
    
    Features:
    - Detect meaningful event sequences
    - Identify attack patterns
    - Temporal ordering
    - Pattern matching
    """
    
    # Known attack patterns
    ATTACK_PATTERNS = {
        "brute_force": {
            "sequence": ["LOGIN_FAILURE", "LOGIN_FAILURE", "LOGIN_SUCCESS"],
            "time_window": 300,  # 5 minutes
            "description": "Multiple failures followed by success",
        },
        "lateral_movement": {
            "sequence": ["LOGIN_SUCCESS", "NETWORK_CONNECTION"],
            "time_window": 600,  # 10 minutes
            "description": "Login followed by network connection",
        },
        "privilege_escalation": {
            "sequence": ["LOGIN_SUCCESS", "PERMISSION_CHANGE"],
            "time_window": 300,
            "description": "Login followed by permission change",
        },
        "data_exfiltration": {
            "sequence": ["FILE_ACCESS", "NETWORK_CONNECTION"],
            "time_window": 3600,
            "description": "File access followed by network connection",
        },
        "command_and_control": {
            "sequence": ["PROCESS_START", "NETWORK_CONNECTION"],
            "time_window": 300,
            "description": "Process start followed by network connection",
        },
        "reconnaissance": {
            "sequence": ["NETWORK_CONNECTION", "NETWORK_CONNECTION", "NETWORK_CONNECTION"],
            "time_window": 120,
            "description": "Multiple network connections (scanning)",
        },
    }
    
    def __init__(self):
        """Initialize the sequence analyzer."""
        self.logger = get_logger("reconstruction.sequence_analyzer")
        self.patterns = self.ATTACK_PATTERNS
    
    def analyze(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze event sequences for attack patterns.
        
        Args:
            events: List of events
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        self.logger.info(f"Analyzing {len(events)} events for sequences")
        
        # Convert to event objects if needed
        event_objects = []
        for event in events:
            if isinstance(event, dict):
                event_objects.append(EventModel(**event))
            else:
                event_objects.append(event)
        
        # Sort by timestamp
        sorted_events = sorted(event_objects, key=lambda x: x.timestamp)
        
        # Group by source
        source_groups = defaultdict(list)
        for event in sorted_events:
            source = event.source_ip or event.source_hostname or "unknown"
            source_groups[source].append(event)
        
        # Analyze each source group
        patterns_detected = []
        for source, source_events in source_groups.items():
            patterns = self._find_patterns(source_events, source)
            patterns_detected.extend(patterns)
        
        # Calculate sequence scores
        sequence_scores = self._calculate_sequence_scores(patterns_detected)
        
        return {
            "total_events": len(events),
            "source_groups": len(source_groups),
            "patterns_detected": patterns_detected,
            "sequence_scores": sequence_scores,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    def _find_patterns(self, events: List[EventModel], source: str) -> List[Dict[str, Any]]:
        """
        Find attack patterns in event sequences.
        
        Args:
            events: List of events (sorted by time)
            source: Source identifier
            
        Returns:
            List[Dict[str, Any]]: Detected patterns
        """
        patterns = []
        
        for pattern_name, pattern_def in self.patterns.items():
            sequence = pattern_def["sequence"]
            time_window = pattern_def["time_window"]
            description = pattern_def["description"]
            
            # Find matches
            matches = self._find_sequence_matches(events, sequence, time_window)
            
            for match in matches:
                patterns.append({
                    "pattern": pattern_name,
                    "description": description,
                    "source": source,
                    "events": [e.event_id for e in match],
                    "count": len(match),
                    "time_window": time_window,
                })
        
        return patterns
    
    def _find_sequence_matches(
        self,
        events: List[EventModel],
        sequence: List[str],
        time_window: int
    ) -> List[List[EventModel]]:
        """
        Find matches for a specific sequence pattern.
        
        Args:
            events: List of events
            sequence: Event type sequence to match
            time_window: Maximum time window
            
        Returns:
            List[List[EventModel]]: Matching sequences
        """
        matches = []
        
        for i in range(len(events) - len(sequence) + 1):
            # Check if sequence matches
            match = True
            for j, expected_type in enumerate(sequence):
                if events[i + j].event_type != expected_type:
                    match = False
                    break
            
            if match:
                # Check time window
                start_time = events[i].timestamp
                end_time = events[i + len(sequence) - 1].timestamp
                time_diff = (end_time - start_time).total_seconds()
                
                if time_diff <= time_window:
                    matches.append(events[i:i + len(sequence)])
        
        return matches
    
    def _calculate_sequence_scores(self, patterns: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate scores for detected patterns.
        
        Args:
            patterns: Detected patterns
            
        Returns:
            Dict[str, float]: Sequence scores
        """
        scores = {
            "total_patterns": len(patterns),
            "pattern_weights": {},
        }
        
        # Weight different patterns
        pattern_weights = {
            "brute_force": 0.7,
            "lateral_movement": 0.85,
            "privilege_escalation": 0.9,
            "data_exfiltration": 0.8,
            "command_and_control": 0.75,
            "reconnaissance": 0.6,
        }
        
        # Aggregate scores
        pattern_counts = defaultdict(int)
        for pattern in patterns:
            pattern_name = pattern.get("pattern")
            if pattern_name:
                pattern_counts[pattern_name] += 1
        
        # Calculate weighted score
        total_score = 0
        total_weight = 0
        
        for pattern, count in pattern_counts.items():
            weight = pattern_weights.get(pattern, 0.5)
            total_score += weight * min(count, 3)  # Cap at 3 occurrences
            total_weight += weight
        
        if total_weight > 0:
            scores["overall_score"] = min(total_score / total_weight, 1.0)
        else:
            scores["overall_score"] = 0.0
        
        scores["pattern_counts"] = dict(pattern_counts)
        
        return scores