from typing import List, Dict, Any, Tuple, Set
import networkx as nx

class GraphUtils:
    """Utility class for graph operations"""
    
    @staticmethod
    def nodes_to_networkx(nodes: List[Dict[str, Any]], 
                         relationships: List[Dict[str, Any]]) -> nx.Graph:
        """Convert Neo4j data to NetworkX graph"""
        G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            node_id = node.get('id')
            if node_id:
                G.add_node(node_id, **node)
        
        # Add edges
        for rel in relationships:
            source = rel.get('source')
            target = rel.get('target')
            if source and target:
                G.add_edge(source, target, **rel)
        
        return G
    
    @staticmethod
    def find_critical_nodes(graph: nx.Graph, top_n: int = 10) -> List[Tuple[str, Dict[str, Any]]]:
        """Find most critical nodes based on degree and centrality"""
        if graph.number_of_nodes() == 0:
            return []
        
        # Calculate degree centrality
        degree_cent = nx.degree_centrality(graph)
        
        # Calculate betweenness centrality
        betweenness_cent = nx.betweenness_centrality(graph)
        
        # Calculate closeness centrality
        closeness_cent = nx.closeness_centrality(graph)
        
        # Combine scores
        scores = {}
        for node in graph.nodes():
            scores[node] = {
                'degree_centrality': degree_cent.get(node, 0),
                'betweenness_centrality': betweenness_cent.get(node, 0),
                'closeness_centrality': closeness_cent.get(node, 0),
                'combined_score': (degree_cent.get(node, 0) + 
                                  betweenness_cent.get(node, 0) + 
                                  closeness_cent.get(node, 0)) / 3
            }
        
        # Sort by combined score
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1]['combined_score'], reverse=True)
        return sorted_nodes[:top_n]
    
    @staticmethod
    def get_community_detection(graph: nx.Graph) -> Dict[str, int]:
        """Detect communities in the graph"""
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            
            communities = greedy_modularity_communities(graph)
            community_map = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_map[node] = i
            
            return community_map
        except ImportError:
            return {}
    
    @staticmethod
    def calculate_graph_metrics(graph: nx.Graph) -> Dict[str, Any]:
        """Calculate various graph metrics"""
        if graph.number_of_nodes() == 0:
            return {}
        
        # Basic metrics
        metrics = {
            'num_nodes': graph.number_of_nodes(),
            'num_edges': graph.number_of_edges(),
            'density': nx.density(graph),
            'is_connected': nx.is_connected(graph),
            'diameter': None,
            'avg_clustering': nx.average_clustering(graph),
            'avg_shortest_path': None
        }
        
        # Calculate diameter if connected
        if metrics['is_connected']:
            try:
                metrics['diameter'] = nx.diameter(graph)
                metrics['avg_shortest_path'] = nx.average_shortest_path_length(graph)
            except:
                metrics['diameter'] = None
                metrics['avg_shortest_path'] = None
        
        return metrics
    
    @staticmethod
    def find_shortest_paths(graph: nx.Graph, source: str, target: str) -> List[List[str]]:
        """Find all shortest paths between two nodes"""
        try:
            return list(nx.all_shortest_paths(graph, source, target))
        except:
            return []
    
    @staticmethod
    def find_attack_paths(graph: nx.Graph, source: str, 
                         target: str, max_depth: int = 5) -> List[List[str]]:
        """Find all possible attack paths up to max_depth"""
        paths = []
        
        def find_paths(current: str, target: str, depth: int, path: List[str]):
            if depth > max_depth:
                return
            if current == target:
                paths.append(path.copy())
                return
            
            neighbors = list(graph.neighbors(current))
            for neighbor in neighbors:
                if neighbor not in path:
                    path.append(neighbor)
                    find_paths(neighbor, target, depth + 1, path)
                    path.pop()
        
        find_paths(source, target, 0, [source])
        return paths
    
    @staticmethod
    def get_attack_surface(graph: nx.Graph, node_id: str, 
                          max_depth: int = 2) -> Set[str]:
        """Get attack surface for a node (reachable nodes within max_depth)"""
        reachable = set()
        
        def dfs(current: str, depth: int):
            if depth > max_depth:
                return
            if current not in reachable:
                reachable.add(current)
                for neighbor in graph.neighbors(current):
                    dfs(neighbor, depth + 1)
        
        dfs(node_id, 0)
        return reachable