"""Asset enrichment using CMDB-like data."""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.enrichers.base import BaseEnricher
from src.models.enriched_event import AssetInfo
from src.core.config import settings


class AssetEnricher(BaseEnricher):
    """
    Enriches events with asset information.
    
    Adds:
    - Asset type (workstation, server, etc.)
    - Owner/department
    - Criticality score
    - Business unit
    - Location
    - Tags
    """
    
    def __init__(self, asset_db_path: Optional[str] = None):
        """
        Initialize asset enricher.
        
        Args:
            asset_db_path: Path to asset database JSON file
        """
        super().__init__(enricher_name="asset-enricher")
        self.asset_db_path = asset_db_path or "data/enrichment_data/assets.json"
        self.assets = {}
        self._load_assets()
    
    def _load_assets(self) -> None:
        """Load asset data from file."""
        if os.path.exists(self.asset_db_path):
            try:
                with open(self.asset_db_path, 'r') as f:
                    self.assets = json.load(f)
                self.logger.info(f"Loaded {len(self.assets)} assets from {self.asset_db_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load assets: {e}")
                self._create_default_assets()
        else:
            self.logger.info("No asset database found, creating default")
            self._create_default_assets()
    
    def _create_default_assets(self) -> None:
        """Create default asset data."""
        self.assets = {
            "192.168.1.10": {
                "asset_id": "ASSET-001",
                "asset_type": "workstation",
                "hostname": "PC-01",
                "owner": "John Doe",
                "department": "Engineering",
                "criticality": 5,
                "business_unit": "North America",
                "location": "Building A, Floor 3",
                "tags": ["windows", "user-workstation"],
            },
            "192.168.1.20": {
                "asset_id": "ASSET-002",
                "asset_type": "server",
                "hostname": "SERVER-01",
                "owner": "IT Team",
                "department": "IT Operations",
                "criticality": 9,
                "business_unit": "Global",
                "location": "Data Center A",
                "tags": ["linux", "production", "critical"],
            },
            "192.168.1.30": {
                "asset_id": "ASSET-003",
                "asset_type": "server",
                "hostname": "SERVER-02",
                "owner": "IT Team",
                "department": "IT Operations",
                "criticality": 8,
                "business_unit": "Global",
                "location": "Data Center A",
                "tags": ["windows", "production", "database"],
            },
            "192.168.1.40": {
                "asset_id": "ASSET-004",
                "asset_type": "database",
                "hostname": "DB-01",
                "owner": "DBA Team",
                "department": "Engineering",
                "criticality": 10,
                "business_unit": "Global",
                "location": "Data Center A",
                "tags": ["database", "critical", "production"],
            },
            "10.0.0.1": {
                "asset_id": "ASSET-005",
                "asset_type": "firewall",
                "hostname": "FW-01",
                "owner": "Security Team",
                "department": "Security",
                "criticality": 10,
                "business_unit": "Global",
                "location": "Data Center A",
                "tags": ["firewall", "critical", "network"],
            },
        }
        
        # Save default assets
        os.makedirs(os.path.dirname(self.asset_db_path), exist_ok=True)
        with open(self.asset_db_path, 'w') as f:
            json.dump(self.assets, f, indent=2)
        
        self.logger.info(f"Created default assets at {self.asset_db_path}")
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with asset information.
        
        Args:
            event: Event data to enrich
            
        Returns:
            Dict[str, Any]: Event with asset enrichment
        """
        if not self.enabled:
            return event
        
        result = event.copy()
        enrichments_applied = []
        
        # Get source and destination IPs
        source_ip = self._get_ip(event, "source")
        dest_ip = self._get_ip(event, "destination")
        
        # Enrich source
        if source_ip and source_ip in self.assets:
            asset_data = self.assets[source_ip]
            result["source_asset"] = AssetInfo(**asset_data).dict()
            enrichments_applied.append("source_asset")
            self.logger.debug(f"Enriched source {source_ip} with asset data")
        
        # Enrich destination
        if dest_ip and dest_ip in self.assets:
            asset_data = self.assets[dest_ip]
            result["destination_asset"] = AssetInfo(**asset_data).dict()
            enrichments_applied.append("destination_asset")
            self.logger.debug(f"Enriched destination {dest_ip} with asset data")
        
        # Update metadata
        if enrichments_applied:
            if "enrichment_applied" not in result:
                result["enrichment_applied"] = []
            result["enrichment_applied"].extend(enrichments_applied)
        
        self._update_stats(success=True, enrichments_count=len(enrichments_applied))
        return result
    
    def _get_ip(self, event: Dict[str, Any], field: str) -> Optional[str]:
        """
        Get IP address from event.
        
        Args:
            event: Event data
            field: Field name (source or destination)
            
        Returns:
            Optional[str]: IP address or None
        """
        # Try direct field
        ip = self._safe_get(event, f"{field}_ip")
        if ip:
            return ip
        
        # Try nested object
        obj = self._safe_get(event, field)
        if obj and isinstance(obj, dict):
            ip = obj.get("ip")
            if ip:
                return ip
        
        # Try with underscores
        ip = self._safe_get(event, f"{field}_address")
        if ip:
            return ip
        
        return None
    
    def add_asset(self, ip: str, asset_data: Dict[str, Any]) -> None:
        """
        Add or update an asset.
        
        Args:
            ip: IP address of the asset
            asset_data: Asset data dictionary
        """
        self.assets[ip] = asset_data
        self._save_assets()
        self.logger.info(f"Added/updated asset {ip}")
    
    def _save_assets(self) -> None:
        """Save assets to file."""
        try:
            os.makedirs(os.path.dirname(self.asset_db_path), exist_ok=True)
            with open(self.asset_db_path, 'w') as f:
                json.dump(self.assets, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save assets: {e}")