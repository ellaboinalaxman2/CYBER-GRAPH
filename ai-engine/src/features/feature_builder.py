"""Feature builder that combines all features."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import json

from src.core.logging import get_logger
from src.core.exceptions import FeatureEngineeringError
from src.features.node_features import NodeFeatureExtractor
from src.features.edge_features import EdgeFeatureExtractor
from src.features.event_features import EventFeatureExtractor
from src.features.temporal_features import TemporalFeatureExtractor
from src.features.feature_normalizer import FeatureNormalizer
from src.models.input_schemas import EventInput, GraphInput, NodeInput, EdgeInput


class FeatureBuilder:
    """
    Combines all feature extractors into a single pipeline.
    
    Features:
    - Node features
    - Edge features
    - Event features
    - Temporal features
    - Feature normalization
    - Feature selection
    - Feature persistence
    """
    
    def __init__(self):
        """Initialize the feature builder."""
        self.logger = get_logger("features.feature_builder")
        
        self.node_extractor = NodeFeatureExtractor()
        self.edge_extractor = EdgeFeatureExtractor()
        self.event_extractor = EventFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()
        self.normalizer = FeatureNormalizer()
        
        self._feature_config = {}
        self._feature_names = []
        self._stats = {
            "nodes_processed": 0,
            "edges_processed": 0,
            "events_processed": 0,
            "features_generated": 0,
            "feature_groups": {},
        }
    
    def build_features(
        self,
        nodes: List[NodeInput],
        edges: Optional[List[EdgeInput]] = None,
        events: Optional[List[EventInput]] = None,
        normalize: bool = True,
        feature_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build complete feature set.
        
        Args:
            nodes: List of nodes
            edges: List of edges
            events: List of events
            normalize: Whether to normalize features
            feature_config: Feature configuration
            
        Returns:
            Dict[str, Any]: Complete feature set
        """
        self.logger.info("Building feature set...")
        
        if feature_config:
            self._feature_config = feature_config
        
        result = {
            "status": "building",
            "features": {},
            "metadata": {},
        }
        
        # ====================================================================
        # Extract node features
        # ====================================================================
        if nodes:
            self.logger.info(f"Extracting node features for {len(nodes)} nodes")
            node_features = self.node_extractor.extract_features(nodes, edges, events)
            result["features"]["node_features"] = node_features
            self._stats["nodes_processed"] = len(nodes)
            self._stats["feature_groups"]["node"] = len(node_features.columns)
        
        # ====================================================================
        # Extract edge features
        # ====================================================================
        if edges:
            self.logger.info(f"Extracting edge features for {len(edges)} edges")
            edge_features = self.edge_extractor.extract_features(edges, events)
            result["features"]["edge_features"] = edge_features
            self._stats["edges_processed"] = len(edges)
            self._stats["feature_groups"]["edge"] = len(edge_features.columns)
        
        # ====================================================================
        # Extract event features
        # ====================================================================
        if events:
            self.logger.info(f"Extracting event features from {len(events)} events")
            event_features = self.event_extractor.extract_features(events)
            result["features"]["event_features"] = event_features
            self._stats["events_processed"] = len(events)
            self._stats["feature_groups"]["event"] = len(event_features.columns)
        
        # ====================================================================
        # Extract temporal features
        # ====================================================================
        if events:
            self.logger.info(f"Extracting temporal features from {len(events)} events")
            temporal_features = self.temporal_extractor.extract_features(events)
            result["features"]["temporal_features"] = temporal_features
            self._stats["feature_groups"]["temporal"] = len(temporal_features.columns)
        
        # ====================================================================
        # Combine features
        # ====================================================================
        combined = self._combine_features(result["features"])
        result["features"]["combined"] = combined
        
        # ====================================================================
        # Normalize features
        # ====================================================================
        if normalize and combined is not None:
            self.logger.info("Normalizing features...")
            normalized = self.normalizer.normalize(combined)
            result["features"]["normalized"] = normalized
            
            # Store normalization parameters
            result["metadata"]["normalization_params"] = self.normalizer.get_params()
        
        # ====================================================================
        # Generate metadata
        # ====================================================================
        result["metadata"] = {
            **result["metadata"],
            "total_nodes": len(nodes) if nodes else 0,
            "total_edges": len(edges) if edges else 0,
            "total_events": len(events) if events else 0,
            "feature_groups": self._stats["feature_groups"],
            "total_features": len(combined.columns) if combined is not None else 0,
            "normalized": normalize,
            "timestamp": pd.Timestamp.utcnow().isoformat(),
        }
        
        self._stats["features_generated"] = len(combined.columns) if combined is not None else 0
        self._feature_names = list(combined.columns) if combined is not None else []
        
        result["status"] = "completed"
        
        self.logger.info(f"Feature building complete! Total features: {self._stats['features_generated']}")
        return result
    
    def _combine_features(self, feature_dict: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Combine all feature DataFrames.
        
        Args:
            feature_dict: Dictionary of feature DataFrames
            
        Returns:
            Optional[pd.DataFrame]: Combined features
        """
        combined = None
        
        # Start with node features
        if "node_features" in feature_dict:
            combined = feature_dict["node_features"].copy()
        
        # Add edge features (aggregated by node)
        if "edge_features" in feature_dict and combined is not None:
            edge_df = feature_dict["edge_features"]
            
            # Aggregate edge features by node
            if 'source_id' in edge_df.columns:
                source_agg = edge_df.groupby('source_id').mean()
                source_agg.columns = [f'edge_out_{col}' for col in source_agg.columns]
                
                target_agg = edge_df.groupby('target_id').mean()
                target_agg.columns = [f'edge_in_{col}' for col in target_agg.columns]
                
                # Merge with combined
                combined = combined.merge(source_agg, left_index=True, right_index=True, how='left')
                combined = combined.merge(target_agg, left_index=True, right_index=True, how='left')
        
        # Add event features
        if "event_features" in feature_dict and combined is not None:
            event_df = feature_dict["event_features"]
            
            # If event features have node_id index, merge
            if 'node_id' in event_df.columns:
                combined = combined.merge(event_df, left_index=True, right_on='node_id', how='left')
        
        # Add temporal features
        if "temporal_features" in feature_dict and combined is not None:
            temp_df = feature_dict["temporal_features"]
            combined = pd.concat([combined, temp_df], axis=1)
        
        # Fill missing values
        if combined is not None:
            combined = combined.fillna(0)
        
        return combined
    
    def save_features(
        self,
        feature_result: Dict[str, Any],
        output_dir: str,
        name: str = "features",
    ) -> Dict[str, str]:
        """
        Save features to disk.
        
        Args:
            feature_result: Feature result from build_features()
            output_dir: Output directory
            name: Name prefix for files
            
        Returns:
            Dict[str, str]: Paths to saved files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        # Save combined features
        combined = feature_result["features"].get("combined")
        if combined is not None:
            combined_path = output_path / f"{name}_combined.parquet"
            combined.to_parquet(combined_path)
            saved_files["combined"] = str(combined_path)
        
        # Save normalized features
        normalized = feature_result["features"].get("normalized")
        if normalized is not None:
            normalized_path = output_path / f"{name}_normalized.parquet"
            normalized.to_parquet(normalized_path)
            saved_files["normalized"] = str(normalized_path)
        
        # Save metadata
        metadata = feature_result.get("metadata", {})
        metadata_path = output_path / f"{name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        saved_files["metadata"] = str(metadata_path)
        
        self.logger.info(f"Saved features to {output_dir}")
        return saved_files
    
    def load_features(self, load_dir: str, name: str = "features") -> Dict[str, Any]:
        """
        Load features from disk.
        
        Args:
            load_dir: Directory to load from
            name: Name prefix for files
            
        Returns:
            Dict[str, Any]: Loaded features
        """
        load_path = Path(load_dir)
        
        loaded = {
            "features": {},
            "metadata": {},
        }
        
        # Load combined features
        combined_path = load_path / f"{name}_combined.parquet"
        if combined_path.exists():
            loaded["features"]["combined"] = pd.read_parquet(combined_path)
        
        # Load normalized features
        normalized_path = load_path / f"{name}_normalized.parquet"
        if normalized_path.exists():
            loaded["features"]["normalized"] = pd.read_parquet(normalized_path)
        
        # Load metadata
        metadata_path = load_path / f"{name}_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                loaded["metadata"] = json.load(f)
        
        self.logger.info(f"Loaded features from {load_dir}")
        return loaded
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get feature building statistics."""
        return self._stats.copy()
    
    def get_feature_names(self) -> List[str]:
        """Get the names of generated features."""
        return self._feature_names.copy()