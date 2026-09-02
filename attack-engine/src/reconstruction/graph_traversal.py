"""Graph traversal for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Set, Tuple
from collections import deque, defaultdict
import networkx as nx

from src.core.logging import get_logger
from src.core.exceptions import ReconstructionError


class GraphTraversal:
    """
    Traverses graph to find paths and relationships.
    
    Features:
    - BFS/DFS traversal
    - Path finding between nodes
    - Neighbor discovery
    - Graph analysis
    """
    
    def __init__(self):
        """Initialize the graph traversal."""
        self.logger = get_logger("reconstruction.graph_traversal")
        self.graph = nx.DiGraph()
    
    def build_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> None:
        """
        Build a graph from nodes and edges.
        
        Args:
            nodes: List of nodes
            edges: List of edges
        """
        self.graph = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            node_id = node.get('id') or node.get('node_id')
            if node_id:
                self.graph.add_node(node_id, **node)
        
        # Add edges
        for edge in edges:
            source = edge.get('source_id') or edge.get('from')
            target = edge.get('target_id') or edge.get('to')
            if source and target:
                self.graph.add_edge(source, target, **edge)
        
        self.logger.info(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def find_path(self, source: str, target: str, max_depth: int = 10) -> List[List[str]]:
        """
        Find all paths between source and target.
        
        Args:
            source: Source node ID
            target: Target node ID
            max_depth: Maximum path depth
            
        Returns:
            List[List[str]]: List of paths
        """
        if source not in self.graph or target not in self.graph:
            return []
        
        try:
            paths = []
            for path in nx.all_simple_paths(self.graph, source, target, cutoff=max_depth):
                paths.append(path)
            return paths
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            self.logger.error(f"Failed to find path: {e}")
            return []
    
    def find_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find the shortest path between source and target.
        
        Args:
            source: Source node ID
            target: Target node ID
            
        Returns:
            Optional[List[str]]: Shortest path
        """
        if source not in self.graph or target not in self.graph:
            return None
        
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            self.logger.error(f"Failed to find shortest path: {e}")
            return None
    
    def get_neighbors(self, node_id: str, depth: int = 1) -> Dict[str, List[str]]:
        """
        Get neighbors of a node.
        
        Args:
            node_id: Node ID
            depth: Neighbor depth
            
        Returns:
            Dict[str, List[str]]: Neighbors by direction
        """
        if node_id not in self.graph:
            return {"in": [], "out": []}
        
        result = {
            "in": [],
            "out": [],
        }
        
        try:
            if depth == 1:
                # Direct neighbors
                result["in"] = list(self.graph.predecessors(node_id))
                result["out"] = list(self.graph.successors(node_id))
            else:
                # Multi-hop neighbors
                in_nodes = set()
                out_nodes = set()
                
                for _ in range(depth):
                    # BFS for incoming
                    new_in = set()
                    for n in result["in"] if result["in"] else [node_id]:
                        new_in.update(self.graph.predecessors(n))
                    in_nodes.update(new_in)
                    
                    # BFS for outgoing
                    new_out = set()
                    for n in result["out"] if result["out"] else [node_id]:
                        new_out.update(self.graph.successors(n))
                    out_nodes.update(new_out)
                
                result["in"] = list(in_nodes - {node_id})
                result["out"] = list(out_nodes - {node_id})
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get neighbors: {e}")
            return {"in": [], "out": []}
    
    def get_connected_components(self) -> List[List[str]]:
        """
        Get connected components of the graph.
        
        Returns:
            List[List[str]]: Connected components
        """
        try:
            components = []
            for component in nx.weakly_connected_components(self.graph):
                components.append(list(component))
            return components
        except Exception as e:
            self.logger.error(f"Failed to get connected components: {e}")
            return []
    
    def get_node_degree(self, node_id: str) -> Dict[str, int]:
        """
        Get degree of a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Dict[str, int]: In-degree and out-degree
        """
        if node_id not in self.graph:
            return {"in": 0, "out": 0}
        
        return {
            "in": self.graph.in_degree(node_id),
            "out": self.graph.out_degree(node_id),
        }
    
    def find_attack_paths(self, source: str, max_depth: int = 5) -> List[Dict[str, Any]]:
        """
        Find all paths that could represent attacks from a source.
        
        Args:
            source: Source node ID
            max_depth: Maximum path depth
            
        Returns:
            List[Dict[str, Any]]: Attack paths with metadata
        """
        if source not in self.graph:
            return []
        
        paths = []
        
        # BFS traversal
        visited = {source}
        queue = deque([(source, [source])])
        
        while queue and len(paths) < 100:
            current, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            # Get successors
            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    
                    # Check if this is a potential attack path (ends at high-value target)
                    if self._is_high_value_target(neighbor):
                        paths.append({
                            "path": new_path,
                            "source": source,
                            "target": neighbor,
                            "length": len(new_path) - 1,
                        })
                    
                    visited.add(neighbor)
                    queue.append((neighbor, new_path))
        
        # Sort by length
        paths.sort(key=lambda x: x["length"])
        
        return paths
    
    def _is_high_value_target(self, node_id: str) -> bool:
        """
        Check if a node is a high-value target.
        
        Args:
            node_id: Node ID
            
        Returns:
            bool: True if high-value target
        """
        if node_id not in self.graph:
            return False
        
        # Check node attributes
        node_data = self.graph.nodes[node_id]
        
        # High-value keywords
        high_value_types = ["database", "server", "db", "database", "critical", "sensitive"]
        node_type = node_data.get("type", "").lower()
        node_device = node_data.get("device_type", "").lower()
        
        # Check if high-value
        for keyword in high_value_types:
            if keyword in node_type or keyword in node_device:
                return True
        
        return False