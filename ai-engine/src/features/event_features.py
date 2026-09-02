"""Event-based feature extraction for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from src.core.logging import get_logger
from src.core.exceptions import FeatureEngineeringError
from src.models.input_schemas import EventInput


class EventFeatureExtractor:
    """
    Extracts features from security events.
    
    Features:
    - Event counts by type
    - Event frequencies
    - Severity distribution
    - Protocol distribution
    - Action distribution
    - Time-based patterns
    """
    
    def __init__(self):
        """Initialize the event feature extractor."""
        self.logger = get_logger("features.event_features")
        self._feature_names = []
        self._stats = {
            "events_processed": 0,
            "features_extracted": 0,
            "time_windows_created": 0,
        }
    
    def extract_features(
        self,
        events: List[EventInput],
        node_id: Optional[str] = None,
        window_minutes: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Extract features from events.
        
        Args:
            events: List of events
            node_id: Optional node ID to filter events
            window_minutes: Optional time window for aggregation
            
        Returns:
            pd.DataFrame: Event features
        """
        if node_id:
            # Filter events for specific node
            filtered_events = [
                e for e in events
                if e.source_ip == node_id or e.destination_ip == node_id or e.hostname == node_id
            ]
        else:
            filtered_events = events
        
        self.logger.info(f"Extracting event features from {len(filtered_events)} events")
        
        if not filtered_events:
            return pd.DataFrame()
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame([e.dict() for e in filtered_events])
        
        # Parse timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Extract features
        if window_minutes:
            features = self._extract_window_features(df, window_minutes)
        else:
            features = self._extract_aggregate_features(df)
        
        self._stats["events_processed"] = len(filtered_events)
        self._stats["features_extracted"] = len(features.columns)
        
        self.logger.info(f"Extracted {len(features.columns)} event features")
        return features
    
    def _extract_aggregate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract aggregate features from events.
        
        Args:
            df: Events DataFrame
            
        Returns:
            pd.DataFrame: Aggregate features
        """
        features = {}
        
        # ====================================================================
        # Event counts
        # ====================================================================
        features['total_events'] = len(df)
        
        # Event type counts
        if 'event_type' in df.columns:
            event_counts = df['event_type'].value_counts()
            for event_type in event_counts.index:
                features[f'count_{event_type}'] = event_counts[event_type]
        
        # Severity counts
        if 'severity' in df.columns:
            severity_counts = df['severity'].value_counts()
            for severity in ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                features[f'severity_{severity}'] = severity_counts.get(severity, 0)
        
        # Protocol counts
        if 'protocol' in df.columns:
            protocol_counts = df['protocol'].value_counts()
            for protocol in ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'SSH', 'FTP', 'DNS']:
                features[f'protocol_{protocol}'] = protocol_counts.get(protocol, 0)
        
        # Action counts
        if 'action' in df.columns:
            action_counts = df['action'].value_counts()
            for action in ['ALLOW', 'DENY', 'BLOCK', 'DROP', 'LOG']:
                features[f'action_{action}'] = action_counts.get(action, 0)
        
        # ====================================================================
        # Ratios and percentages
        # ====================================================================
        total = features['total_events']
        features['severity_high_ratio'] = (features.get('severity_HIGH', 0) + features.get('severity_CRITICAL', 0)) / total
        features['severity_low_ratio'] = (features.get('severity_INFO', 0) + features.get('severity_LOW', 0)) / total
        features['action_deny_ratio'] = (features.get('action_DENY', 0) + features.get('action_BLOCK', 0)) / total
        features['protocol_web_ratio'] = (features.get('protocol_HTTP', 0) + features.get('protocol_HTTPS', 0)) / total
        
        # ====================================================================
        # Diversity metrics
        # ====================================================================
        if 'event_type' in df.columns:
            features['event_type_diversity'] = df['event_type'].nunique()
        if 'severity' in df.columns:
            features['severity_diversity'] = df['severity'].nunique()
        if 'protocol' in df.columns:
            features['protocol_diversity'] = df['protocol'].nunique()
        
        # ====================================================================
        # Unique sources and destinations
        # ====================================================================
        if 'source_ip' in df.columns:
            features['unique_sources'] = df['source_ip'].nunique()
        if 'destination_ip' in df.columns:
            features['unique_destinations'] = df['destination_ip'].nunique()
        
        # ====================================================================
        # Security indicators
        # ====================================================================
        features['has_alerts'] = 1 if features.get('count_ALERT', 0) > 0 else 0
        features['has_login_failures'] = 1 if features.get('count_LOGIN_FAILURE', 0) > 0 else 0
        features['has_firewall_denies'] = 1 if features.get('count_FIREWALL_DENY', 0) > 0 else 0
        
        # Risk score
        risk_score = (
            features.get('count_ALERT', 0) * 0.5 +
            features.get('count_LOGIN_FAILURE', 0) * 0.2 +
            features.get('count_FIREWALL_DENY', 0) * 0.2 +
            features.get('severity_HIGH', 0) * 0.3 +
            features.get('severity_CRITICAL', 0) * 0.5
        )
        features['risk_score'] = min(risk_score / 10.0, 1.0)
        
        # Convert to DataFrame
        return pd.DataFrame([features])
    
    def _extract_window_features(self, df: pd.DataFrame, window_minutes: int) -> pd.DataFrame:
        """
        Extract time-window based features.
        
        Args:
            df: Events DataFrame
            window_minutes: Window size in minutes
            
        Returns:
            pd.DataFrame: Window features
        """
        if 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        # Create time windows
        df['window'] = df['timestamp'].dt.floor(f'{window_minutes}T')
        
        # Group by window
        windows = []
        for window, group in df.groupby('window'):
            window_features = {
                'window_start': window,
                'window_end': window + timedelta(minutes=window_minutes),
                'total_events': len(group),
            }
            
            # Event type counts
            if 'event_type' in group.columns:
                event_counts = group['event_type'].value_counts()
                for event_type in event_counts.index:
                    window_features[f'count_{event_type}'] = event_counts[event_type]
            
            # Severity counts
            if 'severity' in group.columns:
                severity_counts = group['severity'].value_counts()
                for severity in ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                    window_features[f'severity_{severity}'] = severity_counts.get(severity, 0)
            
            # Unique sources and destinations
            if 'source_ip' in group.columns:
                window_features['unique_sources'] = group['source_ip'].nunique()
            if 'destination_ip' in group.columns:
                window_features['unique_destinations'] = group['destination_ip'].nunique()
            
            # Security indicators
            window_features['has_alerts'] = 1 if window_features.get('count_ALERT', 0) > 0 else 0
            window_features['has_login_failures'] = 1 if window_features.get('count_LOGIN_FAILURE', 0) > 0 else 0
            
            windows.append(window_features)
        
        self._stats["time_windows_created"] = len(windows)
        return pd.DataFrame(windows)
    
    def get_feature_names(self) -> List[str]:
        """Get the names of extracted features."""
        return self._feature_names
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get feature extraction statistics."""
        return self._stats.copy()