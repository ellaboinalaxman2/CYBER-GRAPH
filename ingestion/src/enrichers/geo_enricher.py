"""Geographic enrichment using GeoIP data."""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from src.enrichers.base import BaseEnricher
from src.models.enriched_event import GeoInfo


class GeoEnricher(BaseEnricher):
    """
    Enriches events with geographic information.
    
    Adds:
    - Country and country code
    - City and region
    - Latitude/longitude
    - Timezone
    - ISP/Organization
    """
    
    def __init__(self, geo_db_path: Optional[str] = None):
        """
        Initialize geographic enricher.
        
        Args:
            geo_db_path: Path to GeoIP data JSON file
        """
        super().__init__(enricher_name="geo-enricher")
        self.geo_db_path = geo_db_path or "data/enrichment_data/geoip_data.json"
        self.geo_data = {}
        self._load_geo_data()
    
    def _load_geo_data(self) -> None:
        """Load GeoIP data from file."""
        if os.path.exists(self.geo_db_path):
            try:
                with open(self.geo_db_path, 'r') as f:
                    self.geo_data = json.load(f)
                self.logger.info(f"Loaded GeoIP data with {len(self.geo_data)} entries")
            except Exception as e:
                self.logger.warning(f"Failed to load GeoIP data: {e}")
                self._create_default_geo_data()
        else:
            self.logger.info("No GeoIP data found, creating default")
            self._create_default_geo_data()
    
    def _create_default_geo_data(self) -> None:
        """Create default GeoIP data."""
        self.geo_data = {
            "8.8.8.8": {
                "country": "United States",
                "country_code": "US",
                "city": "Mountain View",
                "region": "California",
                "latitude": 37.4223,
                "longitude": -122.0841,
                "timezone": "America/Los_Angeles",
                "isp": "Google LLC",
                "organization": "Google Inc.",
            },
            "1.1.1.1": {
                "country": "United States",
                "country_code": "US",
                "city": "San Francisco",
                "region": "California",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timezone": "America/Los_Angeles",
                "isp": "Cloudflare Inc.",
                "organization": "Cloudflare Inc.",
            },
            "9.9.9.9": {
                "country": "United States",
                "country_code": "US",
                "city": "San Francisco",
                "region": "California",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timezone": "America/Los_Angeles",
                "isp": "Quad9",
                "organization": "Quad9",
            },
            "192.168.1.1": {
                "country": "Private",
                "country_code": "PR",
                "city": "Private Network",
                "region": "Private",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC",
                "isp": "Private",
                "organization": "Private",
            },
        }
        
        # Save default data
        os.makedirs(os.path.dirname(self.geo_db_path), exist_ok=True)
        with open(self.geo_db_path, 'w') as f:
            json.dump(self.geo_data, f, indent=2)
        
        self.logger.info(f"Created default GeoIP data at {self.geo_db_path}")
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with geographic information.
        
        Args:
            event: Event data to enrich
            
        Returns:
            Dict[str, Any]: Event with GeoIP enrichment
        """
        if not self.enabled:
            return event
        
        result = event.copy()
        enrichments_applied = []
        
        # Get source and destination IPs
        source_ip = self._get_ip(event, "source")
        dest_ip = self._get_ip(event, "destination")
        
        # Check if IPs are public (don't geo-enrich private IPs)
        source_geo = self._get_geo_info(source_ip) if source_ip and not self._is_private_ip(source_ip) else None
        dest_geo = self._get_geo_info(dest_ip) if dest_ip and not self._is_private_ip(dest_ip) else None
        
        # Enrich source
        if source_geo:
            result["source_geo"] = source_geo
            enrichments_applied.append("source_geo")
            self.logger.debug(f"Enriched source {source_ip} with GeoIP data")
        
        # Enrich destination
        if dest_geo:
            result["destination_geo"] = dest_geo
            enrichments_applied.append("destination_geo")
            self.logger.debug(f"Enriched destination {dest_ip} with GeoIP data")
        
        # Update metadata
        if enrichments_applied:
            if "enrichment_applied" not in result:
                result["enrichment_applied"] = []
            result["enrichment_applied"].extend(enrichments_applied)
        
        self._update_stats(success=True, enrichments_count=len(enrichments_applied))
        return result
    
    def _get_ip(self, event: Dict[str, Any], field: str) -> Optional[str]:
        """Get IP address from event."""
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
        
        return None
    
    def _get_geo_info(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get geographic information for an IP."""
        if ip in self.geo_data:
            return self.geo_data[ip]
        return None
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private (RFC 1918)."""
        import re
        private_patterns = [
            r'^10\.',
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
            r'^192\.168\.',
            r'^127\.',
            r'^169\.254\.',
        ]
        return any(re.match(pattern, ip) for pattern in private_patterns)
    
    def add_geo_data(self, ip: str, geo_data: Dict[str, Any]) -> None:
        """
        Add or update GeoIP data for an IP.
        
        Args:
            ip: IP address
            geo_data: Geographic data dictionary
        """
        self.geo_data[ip] = geo_data
        self._save_geo_data()
        self.logger.info(f"Added/updated GeoIP data for {ip}")
    
    def _save_geo_data(self) -> None:
        """Save GeoIP data to file."""
        try:
            os.makedirs(os.path.dirname(self.geo_db_path), exist_ok=True)
            with open(self.geo_db_path, 'w') as f:
                json.dump(self.geo_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save GeoIP data: {e}")