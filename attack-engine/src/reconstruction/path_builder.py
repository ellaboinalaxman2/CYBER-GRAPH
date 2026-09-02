"""Path builder for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import ReconstructionError
from src.models.attack_path import AttackPathModel


class PathBuilder:
    """
    Builds attack paths from events and graph data.
    
    Features:
    - Build attack paths from sequences
    - Construct path chains
    - Add metadata to paths
    - Validate paths
    """
    
    def __init__(self):
        """Initialize the path builder."""
        self.logger = get_logger("reconstruction.path_builder")
    
    def build_path(
        self,
        events: List[Dict[str, Any]],
        graph_path: Optional[List[str]] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
    ) -> Optional[AttackPathModel]:
        """
        Build an attack path from events and graph data.
        
        Args:
            events: List of events
            graph_path: Graph path (nodes in order)
            source: Source node
            target: Target node
            
        Returns:
            Optional[AttackPathModel]: Attack path
        """
        self.logger.info(f"Building attack path with {len(events)} events")
        
        # Extract nodes from events
        nodes = self._extract_nodes(events)
        
        # Use graph path if provided
        if graph_path:
            path_nodes = graph_path
        else:
            # Build path from event sequence
            path_nodes = self._build_from_events(events, nodes)
        
        if not path_nodes:
            self.logger.warning("Could not build path from events")
            return None
        
        # Create attack path
        attack_path = AttackPathModel(
            path_id=f"PATH-{datetime.utcnow().timestamp()}",
            nodes=path_nodes,
            edges=self._build_edges(path_nodes),
            source=source or path_nodes[0] if path_nodes else "unknown",
            target=target or path_nodes[-1] if path_nodes else "unknown",
            events=[e.get("event_id") for e in events if e.get("event_id")],
            length=len(path_nodes) - 1 if path_nodes else 0,
        )
        
        self.logger.info(f"Built attack path with {attack_path.length} edges")
        return attack_path
    
    def _extract_nodes(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract nodes from events.
        
        Args:
            events: List of events
            
        Returns:
            Dict[str, Any]: Extracted nodes
        """
        nodes = {}
        
        for event in events:
            source = event.get("source_ip") or event.get("source_hostname")
            destination = event.get("destination_ip") or event.get("destination_hostname")
            
            if source:
                nodes[source] = {
                    "id": source,
                    "type": "device",
                    "ip": event.get("source_ip"),
                    "hostname": event.get("source_hostname"),
                }
            
            if destination:
                nodes[destination] = {
                    "id": destination,
                    "type": "device",
                    "ip": event.get("destination_ip"),
                    "hostname": event.get("destination_hostname"),
                }
        
        return nodes
    
    def _build_from_events(self, events: List[Dict], nodes: Dict) -> List[str]:
        """
        Build path from event sequence.
        
        Args:
            events: List of events
            nodes: Extracted nodes
            
        Returns:
            List[str]: Path nodes
        """
        if not events:
            return []
        
        # Start with source of first event
        path = []
        for event in events:
            source = event.get("source_ip") or event.get("source_hostname")
            dest = event.get("destination_ip") or event.get("destination_hostname")
            
            if source and source not in path:
                path.append(source)
            
            if dest and dest not in path:
                path.append(dest)
        
        return path
    
    def _build_edges(self, nodes: List[str]) -> List[Dict[str, str]]:
        """
        Build edges between nodes.
        
        Args:
            nodes: List of nodes in order
            
        Returns:
            List[Dict[str, str]]: Edges
        """
        edges = []
        for i in range(len(nodes) - 1):
            edges.append({
                "from": nodes[i],
                "to": nodes[i + 1],
                "type": "CONNECTS_TO",
            })
        return edges