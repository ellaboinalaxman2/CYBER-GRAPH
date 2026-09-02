"""Path scoring for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.core.logging import get_logger


class PathScorer:
    """
    Scores attack paths based on various factors.
    
    Features:
    - Score based on events
    - Score based on AI predictions
    - Score based on path characteristics
    - Composite scoring
    """
    
    def __init__(self):
        """Initialize the path scorer."""
        self.logger = get_logger("attack_path.path_scoring")
    
    def score_path(
        self,
        path: List[str],
        events: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None,
    ) -> float:
        """
        Score an attack path.
        
        Args:
            path: Path nodes
            events: List of events
            predictions: AI predictions
            
        Returns:
            float: Path score (0-100)
        """
        if not path:
            return 0.0
        
        score = 0.0
        weights = {
            "anomaly_score": 0.4,
            "event_severity": 0.3,
            "path_length": 0.15,
            "target_criticality": 0.15,
        }
        
        # 1. Anomaly score (from AI predictions)
        anomaly_score = self._get_anomaly_score(path, predictions)
        score += anomaly_score * weights["anomaly_score"]
        
        # 2. Event severity
        event_severity = self._get_event_severity(path, events)
        score += event_severity * weights["event_severity"]
        
        # 3. Path length (longer paths = more suspicious)
        path_length_score = min(len(path) / 5, 1.0)
        score += path_length_score * weights["path_length"]
        
        # 4. Target criticality
        target_criticality = self._get_target_criticality(path)
        score += target_criticality * weights["target_criticality"]
        
        # Normalize to 0-100
        return min(score * 100, 100.0)
    
    def _get_anomaly_score(self, path: List[str], predictions: Optional[List[Dict]] = None) -> float:
        """Get average anomaly score for path nodes."""
        if not predictions:
            return 0.3
        
        scores = []
        for node in path:
            for pred in predictions:
                if pred.get("node_id") == node:
                    scores.append(pred.get("anomaly_score", 0))
                    break
        
        if scores:
            return sum(scores) / len(scores)
        return 0.3
    
    def _get_event_severity(self, path: List[str], events: List[Dict[str, Any]]) -> float:
        """Get event severity score for path."""
        severity_weights = {
            "INFO": 0.1,
            "LOW": 0.2,
            "MEDIUM": 0.5,
            "HIGH": 0.8,
            "CRITICAL": 1.0,
        }
        
        max_severity = 0.0
        for event in events:
            source = event.get("source_ip") or event.get("source_hostname")
            dest = event.get("destination_ip") or event.get("destination_hostname")
            
            if source in path or dest in path:
                severity = event.get("severity", "LOW")
                max_severity = max(max_severity, severity_weights.get(severity, 0.2))
        
        return max_severity
    
    def _get_target_criticality(self, path: List[str]) -> float:
        """Get target criticality score."""
        # Check if path contains critical nodes
        critical_keywords = ["database", "db", "server", "critical", "sensitive", "admin"]
        
        for node in path:
            node_lower = node.lower()
            for keyword in critical_keywords:
                if keyword in node_lower:
                    return 1.0
        
        return 0.5