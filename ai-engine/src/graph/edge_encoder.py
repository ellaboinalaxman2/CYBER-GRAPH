"""Edge encoder for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from sklearn.preprocessing import LabelEncoder

from src.core.logging import get_logger
from src.core.exceptions import GraphConstructionError
from src.models.input_schemas import EdgeInput


class EdgeEncoder:
    """
    Encodes edge properties into numerical features.
    
    Features:
    - Relationship type encoding
    - Protocol encoding
    - Port encoding
    - Frequency normalization
    - Weight normalization
    """
    
    def __init__(self):
        """Initialize the edge encoder."""
        self.logger = get_logger("graph.edge_encoder")
        self._encoders = {}
        self._stats = {
            "edges_encoded": 0,
            "features_created": 0,
            "encoding_columns": [],
        }
    
    def encode_edges(self, edges: List[EdgeInput]) -> pd.DataFrame:
        """
        Encode edges into feature vectors.
        
        Args:
            edges: List of EdgeInput objects
            
        Returns:
            pd.DataFrame: Encoded edge features
        """
        self.logger.info(f"Encoding {len(edges)} edges")
        
        features = []
        
        for edge in edges:
            encoded = self._encode_single_edge(edge)
            features.append(encoded)
        
        df = pd.DataFrame(features)
        
        # Set source_id and target_id as multi-index
        if 'source_id' in df.columns and 'target_id' in df.columns:
            df.set_index(['source_id', 'target_id'], inplace=True)
        
        self._stats["edges_encoded"] = len(edges)
        self._stats["features_created"] = len(df.columns)
        self._stats["encoding_columns"] = df.columns.tolist()
        
        self.logger.info(f"Encoded {len(edges)} edges with {len(df.columns)} features")
        return df
    
    def _encode_single_edge(self, edge: EdgeInput) -> Dict[str, Any]:
        """
        Encode a single edge.
        
        Args:
            edge: EdgeInput object
            
        Returns:
            Dict[str, Any]: Encoded features
        """
        features = {
            'source_id': edge.source_id,
            'target_id': edge.target_id,
        }
        
        # ====================================================================
        # Relationship type encoding (one-hot)
        # ====================================================================
        relationship_types = [
            'CONNECTS_TO', 'ACCESSES', 'AUTHENTICATES_TO',
            'COMMUNICATES_WITH', 'TALKS_TO', 'REACHES',
        ]
        for rt in relationship_types:
            features[f'rel_{rt}'] = 1 if edge.relationship_type == rt else 0
        
        # ====================================================================
        # Weight (normalized 0-1)
        # ====================================================================
        features['weight'] = min(edge.weight or 1.0, 1.0)
        
        # ====================================================================
        # Protocol encoding (one-hot)
        # ====================================================================
        protocol = edge.properties.get('protocol', '')
        protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'SSH', 'FTP', 'DNS', 'UNKNOWN']
        for proto in protocols:
            features[f'protocol_{proto}'] = 1 if protocol == proto else 0
        
        # ====================================================================
        # Port features
        # ====================================================================
        port = edge.properties.get('port', 0)
        
        if port:
            features['port'] = port
            features['is_privileged_port'] = 1 if port < 1024 else 0
            features['is_common_port'] = 1 if port in [22, 80, 443, 3389, 3306, 5432, 8080, 8443] else 0
            features['is_ephemeral_port'] = 1 if 49152 <= port <= 65535 else 0
        else:
            features['port'] = 0
            features['is_privileged_port'] = 0
            features['is_common_port'] = 0
            features['is_ephemeral_port'] = 0
        
        # ====================================================================
        # Frequency (normalized)
        # ====================================================================
        frequency = edge.properties.get('frequency', 0)
        features['frequency'] = min(frequency / 1000.0, 1.0)  # Normalize to 0-1
        
        # ====================================================================
        # Additional properties
        # ====================================================================
        for key, value in edge.properties.items():
            if key not in ['protocol', 'port', 'frequency', 'first_seen', 'last_seen']:
                if isinstance(value, (int, float)):
                    features[f'prop_{key}'] = value
                elif isinstance(value, str):
                    features[f'prop_{key}_exists'] = 1
        
        return features
    
    def get_feature_columns(self) -> List[str]:
        """Get the list of feature column names."""
        return self._stats["encoding_columns"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get encoding statistics."""
        return self._stats.copy()