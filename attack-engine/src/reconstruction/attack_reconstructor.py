"""Attack reconstructor for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import ReconstructionError
from src.models.incident import IncidentModel
from src.models.attack_path import AttackPathModel
from src.reconstruction.path_builder import PathBuilder
from src.reconstruction.graph_traversal import GraphTraversal
from src.reconstruction.sequence_analyzer import SequenceAnalyzer


class AttackReconstructor:
    """
    Reconstructs attacks from events and graph data.
    
    Features:
    - Combine events, AI predictions, and graph
    - Reconstruct attack story
    - Build attack paths
    - Identify attack sequences
    """
    
    def __init__(self):
        """Initialize the attack reconstructor."""
        self.logger = get_logger("reconstruction.attack_reconstructor")
        self.path_builder = PathBuilder()
        self.graph_traversal = GraphTraversal()
        self.sequence_analyzer = SequenceAnalyzer()
    
    def reconstruct(
        self,
        events: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None,
        graph_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Reconstruct an attack from events and graph data.
        
        Args:
            events: List of security events
            predictions: AI predictions for nodes
            graph_data: Graph data (nodes and edges)
            
        Returns:
            Dict[str, Any]: Reconstruction results
        """
        self.logger.info(f"Reconstructing attack from {len(events)} events")
        
        # Build graph if graph data provided
        if graph_data:
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            self.graph_traversal.build_graph(nodes, edges)
        
        # Analyze sequences
        sequence_analysis = self.sequence_analyzer.analyze(events)
        
        # Build attack path
        attack_path = self.path_builder.build_path(events)
        
        # If graph available, find graph paths
        graph_paths = []
        if graph_data and attack_path:
            source = attack_path.source
            target = attack_path.target
            if source and target:
                graph_paths = self.graph_traversal.find_path(source, target)
        
        # Combine results
        result = {
            "status": "success",
            "events_processed": len(events),
            "sequence_analysis": sequence_analysis,
            "attack_path": attack_path.to_dict() if attack_path else None,
            "graph_paths": graph_paths,
            "reconstructed_at": datetime.utcnow().isoformat() + "Z",
        }
        
        # Add AI predictions if available
        if predictions:
            result["predictions"] = predictions
        
        self.logger.info(f"Reconstruction complete: {len(graph_paths)} graph paths found")
        return result
    
    def reconstruct_from_incident(
        self,
        incident: IncidentModel,
        events: List[Dict[str, Any]],
        graph_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Reconstruct attack from an incident.
        
        Args:
            incident: Incident model
            events: List of events
            graph_data: Graph data
            
        Returns:
            Dict[str, Any]: Reconstruction results
        """
        self.logger.info(f"Reconstructing attack from incident {incident.incident_id}")
        
        # Filter events for incident
        incident_events = [e for e in events if e.get("event_id") in incident.event_ids]
        
        # Reconstruct
        return self.reconstruct(incident_events, None, graph_data)