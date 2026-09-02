"""Node encoder for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from sklearn.preprocessing import LabelEncoder

from src.core.logging import get_logger
from src.core.exceptions import GraphConstructionError
from src.models.input_schemas import NodeInput


class NodeEncoder:
    """
    Encodes node properties into numerical features.
    
    Features:
    - One-hot encoding for categorical attributes
    - Label encoding for ordered categories
    - Feature normalization
    - Custom feature mapping
    """
    
    def __init__(self):
        """Initialize the node encoder."""
        self.logger = get_logger("graph.node_encoder")
        self._encoders = {}
        self._feature_mapping = {}
        self._stats = {
            "nodes_encoded": 0,
            "features_created": 0,
            "encoding_columns": [],
        }
    
    def encode_nodes(self, nodes: List[NodeInput]) -> pd.DataFrame:
        """
        Encode nodes into feature vectors.
        
        Args:
            nodes: List of NodeInput objects
            
        Returns:
            pd.DataFrame: Encoded node features
        """
        self.logger.info(f"Encoding {len(nodes)} nodes")
        
        features = []
        
        for node in nodes:
            encoded = self._encode_single_node(node)
            features.append(encoded)
        
        df = pd.DataFrame(features)
        
        # Set node_id as index
        if 'node_id' in df.columns:
            df.set_index('node_id', inplace=True)
        
        self._stats["nodes_encoded"] = len(nodes)
        self._stats["features_created"] = len(df.columns)
        self._stats["encoding_columns"] = df.columns.tolist()
        
        self.logger.info(f"Encoded {len(nodes)} nodes with {len(df.columns)} features")
        return df
    
    def _encode_single_node(self, node: NodeInput) -> Dict[str, Any]:
        """
        Encode a single node.
        
        Args:
            node: NodeInput object
            
        Returns:
            Dict[str, Any]: Encoded features
        """
        features = {
            'node_id': node.node_id,
        }
        
        # ====================================================================
        # Node type encoding (one-hot)
        # ====================================================================
        node_types = ['device', 'user', 'application', 'database', 'firewall', 'router', 'switch', 'unknown']
        for nt in node_types:
            features[f'node_type_{nt}'] = 1 if node.node_type == nt else 0
        
        # ====================================================================
        # Device type encoding (one-hot)
        # ====================================================================
        device_types = ['workstation', 'server', 'firewall', 'router', 'database', 'switch', 'unknown']
        for dt in device_types:
            features[f'device_type_{dt}'] = 1 if node.device_type == dt else 0
        
        # ====================================================================
        # OS encoding (one-hot)
        # ====================================================================
        os_types = ['windows', 'linux', 'macos', 'ubuntu', 'centos', 'debian', 'unknown']
        for os_type in os_types:
            features[f'os_{os_type}'] = 1 if node.os and os_type in node.os.lower() else 0
        
        # ====================================================================
        # Department encoding (label)
        # ====================================================================
        departments = ['Engineering', 'IT', 'Finance', 'HR', 'Security', 'Operations', 'Unknown']
        dept_mapping = {dept: idx for idx, dept in enumerate(departments)}
        features['department_encoded'] = dept_mapping.get(node.department, len(departments) - 1)
        
        # ====================================================================
        # Criticality (normalized 0-1)
        # ====================================================================
        features['criticality'] = node.criticality / 10.0 if node.criticality else 0
        
        # ====================================================================
        # Tag encoding
        # ====================================================================
        common_tags = ['production', 'development', 'testing', 'critical', 'dmz', 'internal', 'external']
        for tag in common_tags:
            features[f'tag_{tag}'] = 1 if tag in node.tags else 0
        
        # ====================================================================
        # Has IP address
        # ====================================================================
        features['has_ip'] = 1 if node.ip_address else 0
        
        # ====================================================================
        # Has hostname
        # ====================================================================
        features['has_hostname'] = 1 if node.hostname else 0
        
        # ====================================================================
        # IP address type (private/public)
        # ====================================================================
        if node.ip_address:
            ip = node.ip_address
            # Check if private IP
            if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.16.') or ip.startswith('172.17.') or ip.startswith('172.18.') or ip.startswith('172.19.') or ip.startswith('172.20.') or ip.startswith('172.21.') or ip.startswith('172.22.') or ip.startswith('172.23.') or ip.startswith('172.24.') or ip.startswith('172.25.') or ip.startswith('172.26.') or ip.startswith('172.27.') or ip.startswith('172.28.') or ip.startswith('172.29.') or ip.startswith('172.30.') or ip.startswith('172.31.'):
                features['is_private_ip'] = 1
            elif ip.startswith('127.'):
                features['is_private_ip'] = 0  # loopback
            else:
                features['is_private_ip'] = 0  # public
        else:
            features['is_private_ip'] = 0
        
        # ====================================================================
        # Additional properties (if any)
        # ====================================================================
        for key, value in node.properties.items():
            if isinstance(value, (int, float)):
                features[f'prop_{key}'] = value
            elif isinstance(value, str):
                # Try to convert to numeric
                try:
                    features[f'prop_{key}'] = float(value)
                except:
                    features[f'prop_{key}_exists'] = 1
        
        return features
    
    def get_feature_columns(self) -> List[str]:
        """Get the list of feature column names."""
        return self._stats["encoding_columns"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get encoding statistics."""
        return self._stats.copy()