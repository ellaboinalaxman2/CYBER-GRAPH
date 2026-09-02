"""Suspicious path detection for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from src.core.logging import get_logger


class SuspiciousPathDetector:
    """
    Detects suspicious paths in the graph.
    
    Features:
    - Identify suspicious paths
    - Score path suspiciousness
    - Detect attack patterns
    - Path validation
    """
    
    def __init__(self):
        """Initialize the suspicious path detector."""
        self.logger = get_logger("attack_path.suspicious_path")
        
        # Suspicious patterns
        self.suspicious_patterns = {
            "lateral_movement": {
                "keywords": ["server", "workstation", "pc"],
                "max_hops": 5,
                "weight": 0.8,
            },
            "privilege_escalation": {
                "keywords": ["admin", "root", "sudo", "privilege"],
                "max_hops": 3,
                "weight": 0.9,
            },
            "data_exfiltration": {
                "keywords": ["database", "db", "data", "export"],
                "max_hops": 4,
                "weight": 0.85,
            },
            "command_control": {
                "keywords": ["external", "public", "internet", "c2"],
                "max_hops": 2,
                "weight": 0.7,
            },
        }
    
    def is_suspicious(
        self,
        path: List[str],
        events: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Check if a path is suspicious.
        
        Args:
            path: Path nodes
            events: List of events
            predictions: AI predictions
            
        Returns:
            bool: True if suspicious
        """
        if not path or len(path) < 2:
            return False
        
        # Check if path contains high-risk nodes
        if self._has_high_risk_nodes(path):
            return True
        
        # Check if path matches suspicious patterns
        if self._matches_suspicious_pattern(path):
            return True
        
        # Check if path has high anomaly scores
        if predictions and self._has_high_anomaly_scores(path, predictions):
            return True
        
        # Check if path has suspicious events
        if self._has_suspicious_events(path, events):
            return True
        
        return False
    
    def get_suspicious_score(
        self,
        path: List[str],
        events: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None,
    ) -> float:
        """
        Get suspicious score for a path.
        
        Args:
            path: Path nodes
            events: List of events
            predictions: AI predictions
            
        Returns:
            float: Suspicious score (0-1)
        """
        if not path:
            return 0.0
        
        score = 0.0
        
        # 1. High-risk nodes (0.3)
        if self._has_high_risk_nodes(path):
            score += 0.3
        
        # 2. Pattern match (0.25)
        pattern_score = self._get_pattern_score(path)
        score += pattern_score * 0.25
        
        # 3. Anomaly scores (0.25)
        if predictions:
            anomaly_score = self._get_anomaly_score(path, predictions)
            score += anomaly_score * 0.25
        
        # 4. Suspicious events (0.2)
        event_score = self._get_event_score(path, events)
        score += event_score * 0.2
        
        return min(score, 1.0)
    
    def _has_high_risk_nodes(self, path: List[str]) -> bool:
        """Check if path contains high-risk nodes."""
        high_risk_keywords = [
            "database", "db", "critical", "sensitive",
            "admin", "root", "secret", "confidential",
        ]
        
        for node in path:
            node_lower = node.lower()
            for keyword in high_risk_keywords:
                if keyword in node_lower:
                    return True
        return False
    
    def _matches_suspicious_pattern(self, path: List[str]) -> bool:
        """Check if path matches suspicious patterns."""
        for pattern_name, pattern in self.suspicious_patterns.items():
            keywords = pattern.get("keywords", [])
            max_hops = pattern.get("max_hops", 5)
            
            if len(path) - 1 > max_hops:
                continue
            
            # Check if any node matches pattern keywords
            for node in path:
                node_lower = node.lower()
                for keyword in keywords:
                    if keyword in node_lower:
                        return True
        
        return False
    
    def _get_pattern_score(self, path: List[str]) -> float:
        """Get pattern matching score."""
        max_score = 0.0
        
        for pattern_name, pattern in self.suspicious_patterns.items():
            keywords = pattern.get("keywords", [])
            weight = pattern.get("weight", 0.5)
            
            # Check matches
            matches = 0
            for node in path:
                node_lower = node.lower()
                for keyword in keywords:
                    if keyword in node_lower:
                        matches += 1
            
            if matches > 0:
                score = min(matches / len(path), 1.0) * weight
                max_score = max(max_score, score)
        
        return max_score
    
    def _has_high_anomaly_scores(
        self,
        path: List[str],
        predictions: List[Dict[str, Any]],
    ) -> bool:
        """Check if path has high anomaly scores."""
        for node in path:
            for pred in predictions:
                if pred.get("node_id") == node:
                    score = pred.get("anomaly_score", 0)
                    if score > 0.7:
                        return True
        return False
    
    def _get_anomaly_score(
        self,
        path: List[str],
        predictions: List[Dict[str, Any]],
    ) -> float:
        """Get average anomaly score for path."""
        scores = []
        for node in path:
            for pred in predictions:
                if pred.get("node_id") == node:
                    scores.append(pred.get("anomaly_score", 0))
                    break
        
        if scores:
            return sum(scores) / len(scores)
        return 0.0
    
    def _has_suspicious_events(self, path: List[str], events: List[Dict[str, Any]]) -> bool:
        """Check if path has suspicious events."""
        suspicious_event_types = [
            "LOGIN_FAILURE", "FIREWALL_DENY", "ALERT",
            "PERMISSION_CHANGE", "USER_MODIFIED",
        ]
        
        for event in events:
            source = event.get("source_ip") or event.get("source_hostname")
            dest = event.get("destination_ip") or event.get("destination_hostname")
            
            if source in path or dest in path:
                event_type = event.get("event_type", "")
                if event_type in suspicious_event_types:
                    return True
        
        return False
    
    def _get_event_score(self, path: List[str], events: List[Dict[str, Any]]) -> float:
        """Get event suspiciousness score."""
        suspicious_event_types = {
            "LOGIN_FAILURE": 0.6,
            "FIREWALL_DENY": 0.7,
            "ALERT": 0.9,
            "PERMISSION_CHANGE": 0.8,
            "USER_MODIFIED": 0.7,
            "FILE_ACCESS": 0.5,
            "NETWORK_CONNECTION": 0.4,
        }
        
        max_score = 0.0
        for event in events:
            source = event.get("source_ip") or event.get("source_hostname")
            dest = event.get("destination_ip") or event.get("destination_hostname")
            
            if source in path or dest in path:
                event_type = event.get("event_type", "")
                score = suspicious_event_types.get(event_type, 0.2)
                max_score = max(max_score, score)
        
        return max_score