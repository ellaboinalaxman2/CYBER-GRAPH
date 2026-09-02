"""Node feature extraction for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Set
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from src.core.logging import get_logger
from src.core.exceptions import FeatureEngineeringError
from src.models.input_schemas import NodeInput, EdgeInput, EventInput


class NodeFeatureExtractor:
    """
    Extracts features from graph nodes.
    
    Features:
    - Connection statistics (degree, unique connections)
    - Security metrics (failed logins, alerts)
    - Protocol diversity
    - Port diversity
    - Asset attributes (criticality, type)
    - Behavioral patterns
    """
    
    def __init__(self):
        """Initialize the node feature extractor."""
        self.logger = get_logger("features.node_features")
        self._feature_names = []
        self._stats = {
            "nodes_processed": 0,
            "features_extracted": 0,
        }
    
    def extract_features(
        self,
        nodes: List[NodeInput],
        edges: Optional[List[EdgeInput]] = None,
        events: Optional[List[EventInput]] = None,
    ) -> pd.DataFrame:
        """
        Extract features for all nodes.
        
        Args:
            nodes: List of nodes
            edges: List of edges (for graph-based features)
            events: List of events (for event-based features)
            
        Returns:
            pd.DataFrame: Node features
        """
        self.logger.info(f"Extracting node features for {len(nodes)} nodes")
        
        features = []
        
        # Build graph structures if edges provided
        edge_dict = defaultdict(list)
        reverse_edge_dict = defaultdict(list)
        if edges:
            for edge in edges:
                edge_dict[edge.source_id].append(edge.target_id)
                reverse_edge_dict[edge.target_id].append(edge.source_id)
        
        # Build event structures if events provided
        event_counts = defaultdict(Counter)
        event_severities = defaultdict(Counter)
        event_protocols = defaultdict(Counter)
        
        if events:
            for event in events:
                # Get node identifier (source or destination)
                node_id = event.source_ip or event.hostname or event.destination_ip
                if node_id:
                    event_counts[node_id][event.event_type] += 1
                    
                    if event.severity:
                        event_severities[node_id][event.severity] += 1
                    
                    if event.protocol:
                        event_protocols[node_id][event.protocol] += 1
        
        # Extract features for each node
        for node in nodes:
            node_features = self._extract_single_node_features(
                node,
                edge_dict,
                reverse_edge_dict,
                event_counts.get(node.node_id, Counter()),
                event_severities.get(node.node_id, Counter()),
                event_protocols.get(node.node_id, Counter()),
            )
            features.append(node_features)
        
        # Convert to DataFrame
        df = pd.DataFrame(features)
        
        # Set node_id as index
        if 'node_id' in df.columns:
            df.set_index('node_id', inplace=True)
        
        self._stats["nodes_processed"] = len(nodes)
        self._stats["features_extracted"] = len(df.columns)
        
        self.logger.info(f"Extracted {len(df.columns)} features for {len(nodes)} nodes")
        return df
    
    def _extract_single_node_features(
        self,
        node: NodeInput,
        edge_dict: Dict[str, List[str]],
        reverse_edge_dict: Dict[str, List[str]],
        event_counts: Counter,
        event_severities: Counter,
        event_protocols: Counter,
    ) -> Dict[str, Any]:
        """
        Extract features for a single node.
        
        Args:
            node: NodeInput object
            edge_dict: Source -> Targets mapping
            reverse_edge_dict: Target -> Sources mapping
            event_counts: Event type counts for this node
            event_severities: Severity counts for this node
            event_protocols: Protocol counts for this node
            
        Returns:
            Dict[str, Any]: Node features
        """
        features = {
            'node_id': node.node_id,
        }
        
        # ====================================================================
        # Graph-based features
        # ====================================================================
        outgoing = edge_dict.get(node.node_id, [])
        incoming = reverse_edge_dict.get(node.node_id, [])
        
        features['degree'] = len(outgoing) + len(incoming)
        features['outgoing_degree'] = len(outgoing)
        features['incoming_degree'] = len(incoming)
        features['unique_neighbors'] = len(set(outgoing + incoming))
        
        # Neighbor diversity
        all_neighbors = set(outgoing + incoming)
        features['neighbor_ratio'] = len(all_neighbors) / (len(all_neighbors) + 1) if all_neighbors else 0
        
        # ====================================================================
        # Asset-based features
        # ====================================================================
        # Criticality (normalized to 0-1)
        features['criticality'] = node.criticality / 10.0 if node.criticality else 0
        
        # Device type encoding
        device_types = ['workstation', 'server', 'firewall', 'router', 'database', 'switch', 'unknown']
        for dt in device_types:
            features[f'is_{dt}'] = 1 if node.device_type and dt in node.device_type.lower() else 0
        
        # OS encoding
        os_types = ['windows', 'linux', 'macos', 'ubuntu', 'centos', 'debian', 'unknown']
        for os_type in os_types:
            features[f'os_{os_type}'] = 1 if node.os and os_type in node.os.lower() else 0
        
        # ====================================================================
        # Event-based features
        # ====================================================================
        # Total events
        total_events = sum(event_counts.values())
        features['total_events'] = total_events
        
        # Event type counts
        event_types = [
            'LOGIN_SUCCESS', 'LOGIN_FAILURE', 'LOGIN_LOCKOUT',
            'NETWORK_CONNECTION', 'NETWORK_DISCONNECTION',
            'FIREWALL_ALLOW', 'FIREWALL_DENY', 'FIREWALL_DROP',
            'ALERT', 'SYSTEM_EVENT', 'FILE_ACCESS', 'FILE_MODIFIED',
            'FILE_DELETED', 'USER_CREATED', 'USER_DELETED', 'USER_MODIFIED',
        ]
        
        for et in event_types:
            features[f'event_{et}'] = event_counts.get(et, 0)
        
        # Login failure ratio
        login_success = event_counts.get('LOGIN_SUCCESS', 0)
        login_failure = event_counts.get('LOGIN_FAILURE', 0)
        total_logins = login_success + login_failure
        features['login_failure_ratio'] = login_failure / (total_logins + 1)
        
        # Alert ratio
        alerts = event_counts.get('ALERT', 0)
        features['alert_ratio'] = alerts / (total_events + 1)
        
        # Severity scores
        severity_weights = {'INFO': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        
        total_severity_score = 0
        for severity, count in event_severities.items():
            total_severity_score += severity_weights.get(severity, 0) * count
        
        features['avg_severity_score'] = total_severity_score / (total_events + 1)
        
        # Severity distribution
        for severity in ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            features[f'severity_{severity}'] = event_severities.get(severity, 0)
        
        # Protocol diversity
        unique_protocols = len(event_protocols)
        features['protocol_diversity'] = unique_protocols
        
        # Protocol counts
        for protocol in ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'SSH', 'FTP', 'DNS']:
            features[f'protocol_{protocol}'] = event_protocols.get(protocol, 0)
        
        # Protocol ratio (most common protocol)
        if event_protocols:
            most_common_protocol = max(event_protocols, key=event_protocols.get)
            features['most_common_protocol'] = most_common_protocol
            features['most_common_protocol_ratio'] = event_protocols[most_common_protocol] / total_events
            
            # Protocol entropy
            probs = [count / total_events for count in event_protocols.values()]
            entropy = -sum(p * np.log(p) for p in probs)
            features['protocol_entropy'] = entropy
        else:
            features['most_common_protocol'] = 'NONE'
            features['most_common_protocol_ratio'] = 0
            features['protocol_entropy'] = 0
        
        # ====================================================================
        # Security risk indicators
        # ====================================================================
        features['has_alerts'] = 1 if alerts > 0 else 0
        features['has_login_failures'] = 1 if login_failure > 0 else 0
        features['has_high_severity'] = 1 if event_severities.get('HIGH', 0) > 0 or event_severities.get('CRITICAL', 0) > 0 else 0
        
        # Risk score (simple combination)
        risk_score = (
            (login_failure * 0.3) +
            (alerts * 0.5) +
            (event_severities.get('HIGH', 0) * 0.7) +
            (event_severities.get('CRITICAL', 0) * 1.0)
        )
        features['risk_score'] = min(risk_score, 1.0)  # Normalize to 0-1
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get the names of extracted features."""
        return self._feature_names
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get feature extraction statistics."""
        return self._stats.copy()