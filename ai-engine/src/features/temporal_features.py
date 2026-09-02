"""Temporal feature extraction for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict

from src.core.logging import get_logger
from src.core.exceptions import FeatureEngineeringError
from src.models.input_schemas import EventInput


class TemporalFeatureExtractor:
    """
    Extracts temporal features from events.
    
    Features:
    - Time of day patterns
    - Day of week patterns
    - Event frequency
    - Burst detection
    - Periodicity
    - Time gaps
    """
    
    def __init__(self):
        """Initialize the temporal feature extractor."""
        self.logger = get_logger("features.temporal_features")
        self._feature_names = []
        self._stats = {
            "events_processed": 0,
            "features_extracted": 0,
            "bursts_detected": 0,
        }
    
    def extract_features(
        self,
        events: List[EventInput],
        node_id: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Extract temporal features from events.
        
        Args:
            events: List of events
            node_id: Optional node ID to filter events
            
        Returns:
            pd.DataFrame: Temporal features
        """
        if node_id:
            filtered_events = [
                e for e in events
                if e.source_ip == node_id or e.destination_ip == node_id or e.hostname == node_id
            ]
        else:
            filtered_events = events
        
        self.logger.info(f"Extracting temporal features from {len(filtered_events)} events")
        
        if not filtered_events:
            return pd.DataFrame()
        
        # Extract timestamps
        timestamps = [e.timestamp for e in filtered_events if e.timestamp]
        
        if not timestamps:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'event_type': [e.event_type for e in filtered_events if e.timestamp],
        })
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Extract features
        features = self._extract_temporal_features(df)
        
        self._stats["events_processed"] = len(filtered_events)
        self._stats["features_extracted"] = len(features)
        
        return pd.DataFrame([features])
    
    def _extract_temporal_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract temporal features from DataFrame.
        
        Args:
            df: Events DataFrame with timestamp column
            
        Returns:
            Dict[str, Any]: Temporal features
        """
        features = {}
        
        # ====================================================================
        # Time distribution features
        # ====================================================================
        # Hour of day
        hours = df['timestamp'].dt.hour
        features['hour_mean'] = hours.mean()
        features['hour_std'] = hours.std()
        features['hour_min'] = hours.min()
        features['hour_max'] = hours.max()
        
        # Most common hour
        most_common_hour = hours.mode()
        features['most_common_hour'] = most_common_hour.iloc[0] if not most_common_hour.empty else 0
        
        # Day of week
        days = df['timestamp'].dt.dayofweek
        features['day_mean'] = days.mean()
        features['day_std'] = days.std()
        
        # Weekend indicator
        features['is_weekend'] = 1 if any(df['timestamp'].dt.dayofweek >= 5) else 0
        
        # Business hours indicator
        business_hours = ((df['timestamp'].dt.hour >= 9) & (df['timestamp'].dt.hour <= 17)).sum()
        features['business_hours_ratio'] = business_hours / len(df)
        
        # ====================================================================
        # Event frequency features
        # ====================================================================
        total_events = len(df)
        features['total_events'] = total_events
        
        # Time span
        time_span = df['timestamp'].max() - df['timestamp'].min()
        features['time_span_seconds'] = time_span.total_seconds()
        
        # Event frequency
        if features['time_span_seconds'] > 0:
            features['events_per_second'] = total_events / features['time_span_seconds']
            features['events_per_minute'] = total_events / (features['time_span_seconds'] / 60)
            features['events_per_hour'] = total_events / (features['time_span_seconds'] / 3600)
        else:
            features['events_per_second'] = total_events
            features['events_per_minute'] = total_events * 60
            features['events_per_hour'] = total_events * 3600
        
        # ====================================================================
        # Time gap features
        # ====================================================================
        if len(df) > 1:
            time_diffs = df['timestamp'].diff().dt.total_seconds().dropna()
            
            features['gap_mean'] = time_diffs.mean()
            features['gap_std'] = time_diffs.std()
            features['gap_min'] = time_diffs.min()
            features['gap_max'] = time_diffs.max()
            features['gap_median'] = time_diffs.median()
            
            # Long gaps (silence periods)
            long_gaps = time_diffs[time_diffs > features['gap_mean'] + features['gap_std']]
            features['long_gap_count'] = len(long_gags)
            features['long_gap_ratio'] = len(long_gaps) / len(time_diffs) if len(time_diffs) > 0 else 0
        else:
            features['gap_mean'] = 0
            features['gap_std'] = 0
            features['gap_min'] = 0
            features['gap_max'] = 0
            features['gap_median'] = 0
            features['long_gap_count'] = 0
            features['long_gap_ratio'] = 0
        
        # ====================================================================
        # Burst detection
        # ====================================================================
        # Simple burst detection: periods with high event frequency
        if len(df) > 10:
            # Calculate rolling event count (5-minute windows)
            window_minutes = 5
            windows = df['timestamp'].dt.floor(f'{window_minutes}T')
            window_counts = windows.value_counts()
            
            burst_threshold = window_counts.mean() + window_counts.std()
            burst_windows = window_counts[window_counts > burst_threshold]
            
            features['burst_count'] = len(burst_windows)
            features['burst_ratio'] = len(burst_windows) / len(window_counts) if len(window_counts) > 0 else 0
            
            # Average burst intensity
            if len(burst_windows) > 0:
                features['avg_burst_intensity'] = burst_windows.mean()
                features['max_burst_intensity'] = burst_windows.max()
            else:
                features['avg_burst_intensity'] = 0
                features['max_burst_intensity'] = 0
            
            self._stats["bursts_detected"] += len(burst_windows)
        else:
            features['burst_count'] = 0
            features['burst_ratio'] = 0
            features['avg_burst_intensity'] = 0
            features['max_burst_intensity'] = 0
        
        # ====================================================================
        # Event type temporal patterns
        # ====================================================================
        if 'event_type' in df.columns:
            # Most common event type at different times
            for hour in range(24):
                hour_events = df[df['timestamp'].dt.hour == hour]
                if len(hour_events) > 0:
                    most_common = hour_events['event_type'].mode()
                    features[f'hour_{hour}_most_common'] = most_common.iloc[0] if not most_common.empty else 'NONE'
                    
                    # Event diversity at this hour
                    features[f'hour_{hour}_diversity'] = hour_events['event_type'].nunique()
            
            # Temporal event type correlation
            # Check if certain event types tend to occur together
            event_time_matrix = pd.crosstab(
                df['timestamp'].dt.floor('1H'),
                df['event_type']
            )
            
            if not event_time_matrix.empty:
                # Correlation between event types
                correlation = event_time_matrix.corr()
                features['max_event_correlation'] = correlation.max().max() if not correlation.empty else 0
        
        # ====================================================================
        # Periodicity detection (simple autocorrelation)
        # ====================================================================
        if len(df) > 24:
            # Hourly aggregation
            hourly_counts = df.groupby(df['timestamp'].dt.floor('1H')).size()
            
            if len(hourly_counts) > 24:
                # Simple periodicity check: compare hour to same hour previous day
                features['has_periodicity'] = 1
                
                # Calculate autocorrelation at lag 24 (daily pattern)
                if len(hourly_counts) > 24:
                    autocorr = hourly_counts.autocorr(lag=24)
                    features['daily_periodicity_strength'] = autocorr if not np.isnan(autocorr) else 0
                else:
                    features['daily_periodicity_strength'] = 0
        else:
            features['has_periodicity'] = 0
            features['daily_periodicity_strength'] = 0
        
        # ====================================================================
        # Normalized time features
        # ====================================================================
        # Normalize hour to 0-1 range
        features['hour_normalized'] = features['hour_mean'] / 24.0
        
        # Normalize gap to 0-1 range
        if features['gap_max'] > 0:
            features['gap_normalized'] = features['gap_mean'] / features['gap_max']
        else:
            features['gap_normalized'] = 0
        
        # Temporal risk score
        temporal_risk = (
            (features['events_per_minute'] / 100) * 0.2 +
            (features['burst_ratio']) * 0.3 +
            (1 - features['business_hours_ratio']) * 0.3 +
            (features['long_gap_ratio']) * 0.2
        )
        features['temporal_risk_score'] = min(temporal_risk, 1.0)
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get the names of extracted features."""
        return self._feature_names
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get feature extraction statistics."""
        return self._stats.copy()