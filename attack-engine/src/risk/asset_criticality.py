"""Asset criticality for Member 5 - Attack Engine."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.core.logging import get_logger


@dataclass
class AssetCriticality:
    """Asset criticality definition."""
    
    asset_type: str
    criticality_score: int  # 1-100
    description: str
    tags: List[str]


class AssetCriticalityManager:
    """
    Manages asset criticality scoring.
    
    Features:
    - Define asset criticality
    - Get criticality by asset type
    - Calculate weighted criticality
    - Update criticality rules
    """
    
    def __init__(self):
        """Initialize the asset criticality manager."""
        self.logger = get_logger("risk.asset_criticality")
        self._criticality_map = self._default_criticality()
    
    def _default_criticality(self) -> Dict[str, AssetCriticality]:
        """Default asset criticality mappings."""
        return {
            "database": AssetCriticality(
                asset_type="database",
                criticality_score=95,
                description="Database servers containing sensitive data",
                tags=["critical", "data", "sensitive"],
            ),
            "db": AssetCriticality(
                asset_type="db",
                criticality_score=95,
                description="Database servers",
                tags=["critical", "data"],
            ),
            "server": AssetCriticality(
                asset_type="server",
                criticality_score=75,
                description="Application servers",
                tags=["production", "application"],
            ),
            "application": AssetCriticality(
                asset_type="application",
                criticality_score=70,
                description="Application servers",
                tags=["production"],
            ),
            "firewall": AssetCriticality(
                asset_type="firewall",
                criticality_score=85,
                description="Firewall and security devices",
                tags=["security", "critical"],
            ),
            "domain_controller": AssetCriticality(
                asset_type="domain_controller",
                criticality_score=90,
                description="Domain controllers",
                tags=["critical", "authentication"],
            ),
            "dc": AssetCriticality(
                asset_type="dc",
                criticality_score=90,
                description="Domain controllers",
                tags=["critical", "authentication"],
            ),
            "workstation": AssetCriticality(
                asset_type="workstation",
                criticality_score=40,
                description="User workstations",
                tags=["user", "endpoint"],
            ),
            "pc": AssetCriticality(
                asset_type="pc",
                criticality_score=40,
                description="User workstations",
                tags=["user", "endpoint"],
            ),
            "laptop": AssetCriticality(
                asset_type="laptop",
                criticality_score=35,
                description="User laptops",
                tags=["user", "endpoint", "mobile"],
            ),
            "printer": AssetCriticality(
                asset_type="printer",
                criticality_score=20,
                description="Printers",
                tags=["peripheral"],
            ),
            "iot": AssetCriticality(
                asset_type="iot",
                criticality_score=15,
                description="IoT devices",
                tags=["iot", "peripheral"],
            ),
            "unknown": AssetCriticality(
                asset_type="unknown",
                criticality_score=30,
                description="Unknown asset type",
                tags=["unknown"],
            ),
        }
    
    def get_criticality(self, asset_type: str) -> AssetCriticality:
        """
        Get criticality for an asset type.
        
        Args:
            asset_type: Asset type
            
        Returns:
            AssetCriticality: Asset criticality
        """
        asset_lower = asset_type.lower()
        
        # Direct match
        if asset_lower in self._criticality_map:
            return self._criticality_map[asset_lower]
        
        # Partial match
        for key, value in self._criticality_map.items():
            if key in asset_lower or asset_lower in key:
                return value
        
        # Default
        return self._criticality_map["unknown"]
    
    def get_criticality_score(self, asset_type: str) -> int:
        """
        Get criticality score for an asset type.
        
        Args:
            asset_type: Asset type
            
        Returns:
            int: Criticality score (1-100)
        """
        return self.get_criticality(asset_type).criticality_score
    
    def get_criticality_for_nodes(self, nodes: List[str]) -> Dict[str, int]:
        """
        Get criticality scores for multiple nodes.
        
        Args:
            nodes: List of node identifiers
            
        Returns:
            Dict[str, int]: Node to criticality mapping
        """
        criticalities = {}
        
        for node in nodes:
            # Try to determine asset type from node name
            asset_type = self._guess_asset_type(node)
            criticalities[node] = self.get_criticality_score(asset_type)
        
        return criticalities
    
    def _guess_asset_type(self, node: str) -> str:
        """
        Guess asset type from node name.
        
        Args:
            node: Node identifier
            
        Returns:
            str: Guessed asset type
        """
        node_lower = node.lower()
        
        if "db" in node_lower or "database" in node_lower or "sql" in node_lower:
            return "database"
        elif "domain" in node_lower or "dc" in node_lower:
            return "domain_controller"
        elif "firewall" in node_lower or "fw" in node_lower:
            return "firewall"
        elif "server" in node_lower or "srv" in node_lower or "app" in node_lower:
            return "server"
        elif "workstation" in node_lower or "pc" in node_lower or "laptop" in node_lower:
            return "workstation"
        elif "printer" in node_lower:
            return "printer"
        elif "iot" in node_lower:
            return "iot"
        else:
            return "unknown"
    
    def add_criticality(self, asset_type: str, criticality: AssetCriticality) -> None:
        """
        Add or update asset criticality.
        
        Args:
            asset_type: Asset type
            criticality: Asset criticality definition
        """
        self._criticality_map[asset_type.lower()] = criticality
        self.logger.info(f"Added criticality for {asset_type}: {criticality.criticality_score}")
    
    def get_all_criticalities(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all criticality definitions.
        
        Returns:
            Dict[str, Dict[str, Any]]: All criticalities
        """
        return {
            key: {
                "asset_type": value.asset_type,
                "criticality_score": value.criticality_score,
                "description": value.description,
                "tags": value.tags,
            }
            for key, value in self._criticality_map.items()
        }
    
    def get_max_criticality(self, nodes: List[str]) -> int:
        """
        Get maximum criticality among nodes.
        
        Args:
            nodes: List of node identifiers
            
        Returns:
            int: Maximum criticality score
        """
        if not nodes:
            return 0
        
        max_score = 0
        for node in nodes:
            asset_type = self._guess_asset_type(node)
            score = self.get_criticality_score(asset_type)
            max_score = max(max_score, score)
        
        return max_score
    
    def get_average_criticality(self, nodes: List[str]) -> float:
        """
        Get average criticality among nodes.
        
        Args:
            nodes: List of node identifiers
            
        Returns:
            float: Average criticality score
        """
        if not nodes:
            return 0.0
        
        total = 0
        for node in nodes:
            asset_type = self._guess_asset_type(node)
            total += self.get_criticality_score(asset_type)
        
        return total / len(nodes)