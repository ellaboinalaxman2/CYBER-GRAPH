from typing import Optional, List, Dict, Any, Union
import json
from datetime import datetime

class CypherBuilder:
    """Helper class for building Cypher queries programmatically"""
    
    @staticmethod
    def create_node(node_type: str, properties: Dict[str, Any]) -> str:
        """Build CREATE node query"""
        props = json.dumps(properties, default=str)
        return f"CREATE (n:{node_type} {props}) RETURN n"
    
    @staticmethod
    def match_node(node_type: str, properties: Dict[str, Any]) -> str:
        """Build MATCH node query"""
        where_clauses = []
        for key, value in properties.items():
            if isinstance(value, str):
                where_clauses.append(f"n.{key} = '{value}'")
            else:
                where_clauses.append(f"n.{key} = {value}")
        
        where_clause = " AND ".join(where_clauses)
        return f"MATCH (n:{node_type} WHERE {where_clause}) RETURN n"
    
    @staticmethod
    def create_relationship(source_id: str, target_id: str, 
                           rel_type: str, properties: Dict[str, Any]) -> str:
        """Build CREATE relationship query"""
        props = json.dumps(properties, default=str)
        return f"""
        MATCH (source {{id: '{source_id}'}})
        MATCH (target {{id: '{target_id}'}})
        CREATE (source)-[r:{rel_type} {props}]->(target)
        RETURN r
        """
    
    @staticmethod
    def find_path(source_id: str, target_id: str, 
                  max_depth: int = 5) -> str:
        """Build path finding query"""
        return f"""
        MATCH (source {{id: '{source_id}'}})
        MATCH (target {{id: '{target_id}'}})
        MATCH path = shortestPath((source)-[*1..{max_depth}]-(target))
        RETURN path
        """
    
    @staticmethod
    def get_neighbors(node_id: str, relationship_type: Optional[str] = None) -> str:
        """Build neighbor query"""
        rel_filter = f":{relationship_type}" if relationship_type else ""
        return f"""
        MATCH (n {{id: '{node_id}'}})-[r{rel_filter}]-(neighbor)
        RETURN neighbor, type(r) as relationship_type
        """
    
    @staticmethod
    def build_where_clause(conditions: Dict[str, Any]) -> str:
        """Build WHERE clause from conditions"""
        if not conditions:
            return ""
        
        clauses = []
        for key, value in conditions.items():
            if isinstance(value, dict):
                # Handle operators like $gte, $lte, etc.
                for op, val in value.items():
                    if op == "$gte":
                        clauses.append(f"n.{key} >= {val}")
                    elif op == "$lte":
                        clauses.append(f"n.{key} <= {val}")
                    elif op == "$gt":
                        clauses.append(f"n.{key} > {val}")
                    elif op == "$lt":
                        clauses.append(f"n.{key} < {val}")
                    elif op == "$in":
                        clauses.append(f"n.{key} IN {val}")
            else:
                clauses.append(f"n.{key} = {value if not isinstance(value, str) else f\"'{value}'\""})
        
        return "WHERE " + " AND ".join(clauses) if clauses else ""

class CypherResultParser:
    """Helper class for parsing Cypher query results"""
    
    @staticmethod
    def parse_node(result: Any) -> Optional[Dict[str, Any]]:
        """Parse node from result"""
        if not result:
            return None
        
        if hasattr(result, 'get'):
            # Result is a dict-like object
            node = result.get('n')
            if node:
                return dict(node)
        elif isinstance(result, dict):
            return result.get('n')
        
        return None
    
    @staticmethod
    def parse_nodes(results: List[Any]) -> List[Dict[str, Any]]:
        """Parse multiple nodes from results"""
        nodes = []
        for result in results:
            if hasattr(result, 'get'):
                node = result.get('n')
                if node:
                    nodes.append(dict(node))
            elif isinstance(result, dict):
                node = result.get('n')
                if node:
                    nodes.append(node)
        return nodes
    
    @staticmethod
    def parse_relationship(result: Any) -> Optional[Dict[str, Any]]:
        """Parse relationship from result"""
        if not result:
            return None
        
        if hasattr(result, 'get'):
            rel = result.get('r')
            if rel:
                return dict(rel)
        elif isinstance(result, dict):
            return result.get('r')
        
        return None
    
    @staticmethod
    def parse_path(result: Any) -> Dict[str, Any]:
        """Parse path from result"""
        if not result:
            return {}
        
        path = result.get('path') if hasattr(result, 'get') else result.get('path', {})
        
        if not path:
            return {}
        
        return {
            'nodes': [dict(node) for node in path.nodes],
            'relationships': [dict(rel) for rel in path.relationships],
            'length': len(path.relationships)
        }
    
    @staticmethod
    def parse_statistics(result: Any) -> Dict[str, Any]:
        """Parse statistics from result"""
        if not result:
            return {}
        
        return dict(result) if hasattr(result, 'items') else {}