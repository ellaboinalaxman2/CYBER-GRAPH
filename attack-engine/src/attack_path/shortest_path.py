"""Shortest path finder for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional, Set
from collections import deque

from src.core.logging import get_logger


class ShortestPathFinder:
    """
    Finds shortest paths in a graph.
    
    Features:
    - BFS shortest path
    - Multiple path finding
    - Path validation
    """
    
    def __init__(self):
        """Initialize the shortest path finder."""
        self.logger = get_logger("attack_path.shortest_path")
    
    def find(self, graph: Dict[str, List[str]], source: str, target: str) -> Optional[List[str]]:
        """
        Find the shortest path between source and target.
        
        Args:
            graph: Graph adjacency list
            source: Source node
            target: Target node
            
        Returns:
            Optional[List[str]]: Shortest path
        """
        if source not in graph or target not in graph:
            return None
        
        if source == target:
            return [source]
        
        # BFS
        visited = {source}
        queue = deque([(source, [source])])
        
        while queue:
            node, path = queue.popleft()
            
            for neighbor in graph.get(node, []):
                if neighbor == target:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def find_all(
        self,
        graph: Dict[str, List[str]],
        source: str,
        target: str,
        max_depth: int = 10,
        max_paths: int = 10
    ) -> List[List[str]]:
        """
        Find all paths between source and target.
        
        Args:
            graph: Graph adjacency list
            source: Source node
            target: Target node
            max_depth: Maximum path depth
            max_paths: Maximum number of paths
            
        Returns:
            List[List[str]]: All paths
        """
        if source not in graph or target not in graph:
            return []
        
        paths = []
        self._dfs(graph, source, target, [source], paths, max_depth)
        
        # Sort by length and limit
        paths.sort(key=len)
        return paths[:max_paths]
    
    def _dfs(
        self,
        graph: Dict[str, List[str]],
        current: str,
        target: str,
        path: List[str],
        paths: List[List[str]],
        max_depth: int
    ) -> None:
        """DFS for finding all paths."""
        if len(path) > max_depth:
            return
        
        if current == target:
            paths.append(path.copy())
            return
        
        for neighbor in graph.get(current, []):
            if neighbor not in path:
                path.append(neighbor)
                self._dfs(graph, neighbor, target, path, paths, max_depth)
                path.pop()