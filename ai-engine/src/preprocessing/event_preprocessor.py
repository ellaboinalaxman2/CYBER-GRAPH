"""Event preprocessor for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import PreprocessingError
from src.models.input_schemas import EventInput


class EventPreprocessor:
    """
    Preprocesses security events for ML.
    
    Features:
    - Event aggregation
    - Feature extraction from events
    - Event normalization
    - Time-based features
    """
    
    def __init__(self):
        """Initialize the event preprocessor."""
        self.logger = get_logger("preprocessing.event_preprocessor")
        self._stats = {
            "events_processed": 0,
            "events_filtered": 0,
            "features_extracted": 0,
        }
    
    def preprocess(self, events: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Preprocess a list of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            pd.DataFrame: Preprocessed event features
        """
        if not events:
            return pd.DataFrame()
        
        self.logger.info(f"Preprocessing {len(events)} events")
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        self._stats["events_processed"] = len(df)
        
        # Extract features
        features = self._extract_features(df)
        
        # Add temporal features
        features = self._add_temporal_features(features)
        
        # Normalize
        features = self._normalize_features(features)
        
        self._stats["features_extracted"] = len(features.columns)
        self.logger.info(f"Extracted {len(features.columns)} features from events")
        
        return features
    
    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from events DataFrame."""
        features = pd.DataFrame()
        
        # Group by node (source or destination)
        for node_field in ['source_ip', 'destination_ip', 'hostname']:
            if node_field in df.columns:
                # Count events per node
                counts = df[node_field].value_counts()
                features[f'{node_field}_event_count'] = df[node_field].map(counts)
        
        # Event type features
        if 'event_type' in df.columns:
            # One-hot encode event types
            event_dummies = pd.get_dummies(df['event_type'], prefix='event')
            features = pd.concat([features, event_dummies], axis=1)
        
        # Severity features
        if 'severity' in df.columns:
            severity_mapping = {'INFO': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
            features['severity_score'] = df['severity'].map(severity_mapping).fillna(0)
        
        # Protocol features
        if 'protocol' in df.columns:
            protocol_dummies = pd.get_dummies(df['protocol'], prefix='protocol')
            features = pd.concat([features, protocol_dummies], axis=1)
        
        # Action features
        if 'action' in df.columns:
            action_dummies = pd.get_dummies(df['action'], prefix='action')
            features = pd.concat([features, action_dummies], axis=1)
        
        # Port features
        for port_field in ['source_port', 'destination_port']:
            if port_field in df.columns:
                # Binary indicator for privileged ports (<1024)
                features[f'{port_field}_is_privileged'] = (df[port_field] < 1024).astype(int)
                
                # Binary indicator for common ports
                common_ports = [22, 80, 443, 3389, 3306, 5432]
                features[f'{port_field}_is_common'] = df[port_field].isin(common_ports).astype(int)
        
        return features
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add temporal features."""
        features = df.copy()
        
        # If timestamp exists, extract time features
        if 'timestamp' in features.columns:
            timestamps = pd.to_datetime(features['timestamp'], utc=True)
            
            features['hour_of_day'] = timestamps.dt.hour
            features['day_of_week'] = timestamps.dt.dayofweek
            features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
            features['is_business_hours'] = ((features['hour_of_day'] >= 9) & 
                                              (features['hour_of_day'] <= 17)).astype(int)
            
            # Time since midnight (in seconds)
            features['seconds_since_midnight'] = (
                timestamps.dt.hour * 3600 + 
                timestamps.dt.minute * 60 + 
                timestamps.dt.second
            )
        
        return features
    
    def _normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize features."""
        features = df.copy()
        
        # Normalize numeric features
        numeric_cols = features.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Skip binary columns
            if features[col].nunique() <= 2:
                continue
            
            # Min-max normalization
            min_val = features[col].min()
            max_val = features[col].max()
            
            if max_val > min_val:
                features[col] = (features[col] - min_val) / (max_val - min_val)
            else:
                features[col] = 0
        
        return features
    
    def aggregate_events(
        self,
        events: List[Dict[str, Any]],
        window_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Aggregate events into time windows.
        
        Args:
            events: List of events
            window_minutes: Window size in minutes
            
        Returns:
            List[Dict[str, Any]]: Aggregated events
        """
        if not events:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        
        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Create time windows
        df['window'] = df['timestamp'].dt.floor(f'{window_minutes}T')
        
        # Aggregate
        aggregated = []
        
        for window, group in df.groupby('window'):
            agg_event = {
                'window_start': window.isoformat() + 'Z',
                'window_end': (window + pd.Timedelta(minutes=window_minutes)).isoformat() + 'Z',
                'total_events': len(group),
                'event_types': group['event_type'].value_counts().to_dict(),
                'severities': group['severity'].value_counts().to_dict() if 'severity' in group else {},
                'unique_sources': group['source_ip'].nunique() if 'source_ip' in group else 0,
                'unique_destinations': group['destination_ip'].nunique() if 'destination_ip' in group else 0,
                'protocols': group['protocol'].value_counts().to_dict() if 'protocol' in group else {},
                'actions': group['action'].value_counts().to_dict() if 'action' in group else {},
            }
            aggregated.append(agg_event)
        
        self.logger.info(f"Aggregated {len(events)} events into {len(aggregated)} windows")
        return aggregated
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get preprocessing statistics."""
        return self._stats.copy()