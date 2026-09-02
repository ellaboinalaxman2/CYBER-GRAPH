"""Path engine for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import ReconstructionError
from src.models.attack_path import AttackPathModel
from src.attack_path.shortest_path import ShortestPathFinder
from src.attack_path.suspicious_path import SuspiciousPathDetector
from src.attack_path.path_scoring import PathScorer


class PathEngine:
    """
    Main path engine for attack path analysis.
    
    Features:
    - Find attack paths
    - Score paths
    - Identify suspicious paths
    - Path analysis
    """
    
    def __init__(self):
        """Initialize the path engine."""
        self.logger = get_logger("attack_path.path_engine")
        self.shortest_path = ShortestPathFinder()
        self.suspicious_path = SuspiciousPathDetector()
        self.path_scorer = PathScorer()
    
    def analyze_paths(
        self,
        events: List[Dict[str, Any]],
        graph_data: Dict[str, Any],
        predictions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze attack paths.
        
        Args:
            events: List of events
            graph_data: Graph data
            predictions: AI predictions
            
        Returns:
            Dict[str, Any]: Path analysis results
        """
        self.logger.info(f"Analyzing paths for {len(events)} events")
        
        # Extract nodes from events
        nodes = self._extract_nodes(events)
        
        # Build graph
        graph = self._build_graph(graph_data)
        
        # Find paths between suspicious nodes
        suspicious_nodes = self._find_suspicious_nodes(nodes, predictions)
        
        paths = []
        for source in suspicious_nodes:
            for target in suspicious_nodes:
                if source != target:
                    path = self.shortest_path.find(graph, source, target)
                    if path:
                        # Score the path
                        score = self.path_scorer.score_path(path, events, predictions)
                        
                        # Check if suspicious
                        is_suspicious = self.suspicious_path.is_suspicious(path, events, predictions)
                        
                        paths.append({
                            "path": path,
                            "score": score,
                            "is_suspicious": is_suspicious,
                            "source": source,
                            "target": target,
                            "length": len(path) - 1,
                        })
        
        # Sort by score (descending)
        paths.sort(key=lambda x: x["score"], reverse=True)
        
        # Get top suspicious paths
        suspicious_paths = [p for p in paths if p["is_suspicious"]]
        
        return {
            "total_paths": len(paths),
            "suspicious_paths": suspicious_paths,
            "top_path": suspicious_paths[0] if suspicious_paths else None,
            "path_count": len(paths),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    def _extract_nodes(self, events: List[Dict[str, Any]]) -> List[str]:
        """Extract nodes from events."""
        nodes = set()
        for event in events:
            source = event.get("source_ip") or event.get("source_hostname")
            dest = event.get("destination_ip") or event.get("destination_hostname")
            if source:
                nodes.add(source)
            if dest:
                nodes.add(dest)
        return list(nodes)
    
    def _build_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build graph from graph data."""
        graph = {}
        
        # Build adjacency list
        for edge in graph_data.get("edges", []):
            source = edge.get("source_id") or edge.get("from")
            target = edge.get("target_id") or edge.get("to")
            
            if source and target:
                if source not in graph:
                    graph[source] = []
                graph[source].append(target)
        
        return graph
    
    def _find_suspicious_nodes(
        self,
        nodes: List[str],
        predictions: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Find suspicious nodes."""
        suspicious = []
        
        # Check predictions
        if predictions:
            for pred in predictions:
                node_id = pred.get("node_id")
                anomaly_score = pred.get("anomaly_score", 0)
                
                if node_id and anomaly_score > 0.5:
                    suspicious.append(node_id)
        
        # If no suspicious nodes found, use all nodes
        if not suspicious:
            suspicious = nodes
        
        return suspicious