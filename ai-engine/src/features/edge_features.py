"""Edge feature extraction for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from datetime import datetime, timedelta

from src.core.logging import get_logger
from src.core.exceptions import FeatureEngineeringError
from src.models.input_schemas import EdgeInput, EventInput


class EdgeFeatureExtractor:
    """
    Extracts features from graph edges.
    
    Features:
    - Communication frequency
    - Protocol information
    - Temporal patterns
    - Security metrics
    - Relationship strength
    """
    
    def __init__(self):
        """Initialize the edge feature extractor."""
        self.logger = get_logger("features.edge_features")
        self._feature_names = []
        self._stats = {
            "edges_processed": 0,
            "features_extracted": 0,
        }
    
    def extract_features(
        self,
        edges: List[EdgeInput],
        events: Optional[List[EventInput]] = None,
    ) -> pd.DataFrame:
        """
        Extract features for all edges.
        
        Args:
            edges: List of edges
            events: List of events (for event-based features)
            
        Returns:
            pd.DataFrame: Edge features
        """
        self.logger.info(f"Extracting edge features for {len(edges)} edges")
        
        features = []
        
        # Build event structures if events provided
        edge_events = defaultdict(list)
        if events:
            for event in events:
                # Create edge key from source and destination
                source = event.source_ip or event.hostname
                dest = event.destination_ip
                if source and dest:
                    edge_key = (source, dest)
                    edge_events[edge_key].append(event)
        
        # Extract features for each edge
        for edge in edges:
            edge_key = (edge.source_id, edge.target_id)
            edge_events_list = edge_events.get(edge_key, [])
            
            edge_features = self._extract_single_edge_features(
                edge,
                edge_events_list,
            )
            features.append(edge_features)
        
        # Convert to DataFrame
        df = pd.DataFrame(features)
        
        # Set edge as index
        if 'source_id' in df.columns and 'target_id' in df.columns:
            df.set_index(['source_id', 'target_id'], inplace=True)
        
        self._stats["edges_processed"] = len(edges)
        self._stats["features_extracted"] = len(df.columns)
        
        self.logger.info(f"Extracted {len(df.columns)} features for {len(edges)} edges")
        return df
    
    def _extract_single_edge_features(
        self,
        edge: EdgeInput,
        events: List[EventInput],
    ) -> Dict[str, Any]:
        """
        Extract features for a single edge.
        
        Args:
            edge: EdgeInput object
            events: Events associated with this edge
            
        Returns:
            Dict[str, Any]: Edge features
        """
        features = {
            'source_id': edge.source_id,
            'target_id': edge.target_id,
        }
        
        # ====================================================================
        # Basic edge properties
        # ====================================================================
        features['weight'] = edge.weight or 1.0
        
        # Relationship type encoding
        relationship_types = [
            'CONNECTS_TO', 'ACCESSES', 'AUTHENTICATES_TO',
            'COMMUNICATES_WITH', 'TALKS_TO', 'REACHES',
        ]
        for rt in relationship_types:
            features[f'rel_{rt}'] = 1 if edge.relationship_type == rt else 0
        
        # ====================================================================
        # Protocol features
        # ====================================================================
        protocol = edge.properties.get('protocol', '')
        port = edge.properties.get('port', 0)
        frequency = edge.properties.get('frequency', 0)
        
        # Protocol encoding
        protocol_enc = {
            'TCP': 1, 'UDP': 2, 'ICMP': 3, 'HTTP': 4,
            'HTTPS': 5, 'SSH': 6, 'FTP': 7, 'DNS': 8,
        }
        features['protocol_encoded'] = protocol_enc.get(protocol, 0)
        
        # Is common protocol
        features['is_common_protocol'] = 1 if protocol in ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH'] else 0
        
        # Port features
        features['port'] = port
        features['is_privileged_port'] = 1 if port and port < 1024 else 0
        features['is_common_port'] = 1 if port in [22, 80, 443, 3389, 3306, 5432] else 0
        
        # Frequency
        features['frequency'] = frequency
        
        # ====================================================================
        # Event-based features
        # ====================================================================
        total_events = len(events)
        features['total_events'] = total_events
        
        # Event type distribution
        event_types = Counter([e.event_type for e in events])
        
        # Security events
        features['login_events'] = event_types.get('LOGIN_SUCCESS', 0) + event_types.get('LOGIN_FAILURE', 0)
        features['alert_events'] = event_types.get('ALERT', 0)
        features['network_events'] = event_types.get('NETWORK_CONNECTION', 0)
        features['firewall_events'] = event_types.get('FIREWALL_ALLOW', 0) + event_types.get('FIREWALL_DENY', 0)
        
        # Event ratios
        features['alert_ratio'] = features['alert_events'] / (total_events + 1)
        features['login_ratio'] = features['login_events'] / (total_events + 1)
        
        # ====================================================================
        # Temporal features
        # ====================================================================
        if events:
            # First and last seen
            timestamps = [e.timestamp for e in events if e.timestamp]
            if timestamps:
                features['first_seen'] = min(timestamps)
                features['last_seen'] = max(timestamps)
                
                # Duration
                if len(timestamps) > 1:
                    features['duration_seconds'] = (max(timestamps) - min(timestamps)).total_seconds()
                else:
                    features['duration_seconds'] = 0
                
                # Event frequency (events per minute)
                if features['duration_seconds'] > 0:
                    features['events_per_minute'] = total_events / (features['duration_seconds'] / 60)
                else:
                    features['events_per_minute'] = total_events
            else:
                features['first_seen'] = None
                features['last_seen'] = None
                features['duration_seconds'] = 0
                features['events_per_minute'] = 0
        else:
            features['first_seen'] = None
            features['last_seen'] = None
            features['duration_seconds'] = 0
            features['events_per_minute'] = 0
        
        # ====================================================================
        # Security risk indicators
        # ====================================================================
        features['has_alerts'] = 1 if features['alert_events'] > 0 else 0
        features['has_login_failures'] = 1 if any(e.event_type == 'LOGIN_FAILURE' for e in events) else 0
        
        # Suspicious score (simple combination)
        suspicious_score = (
            (features['alert_ratio'] * 0.4) +
            (features['login_ratio'] * 0.2) +
            (features['is_common_port'] * 0.1) +
            (1 if features['has_alerts'] else 0) * 0.3
        )
        features['suspicious_score'] = min(suspicious_score, 1.0)
        
        # ====================================================================
        # Metadata features
        # ====================================================================
        # Additional properties
        for key, value in edge.properties.items():
            if key not in ['protocol', 'port', 'frequency', 'first_seen']:
                if isinstance(value, (int, float)):
                    features[f'prop_{key}'] = value
                elif isinstance(value, str):
                    features[f'prop_{key}_exists'] = 1
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get the names of extracted features."""
        return self._feature_names
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get feature extraction statistics."""
        return self._stats.copy()