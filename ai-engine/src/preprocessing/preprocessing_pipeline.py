"""Complete preprocessing pipeline for Member 3 - AI Engine."""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import PreprocessingError
from src.preprocessing.data_cleaner import DataCleaner
from src.preprocessing.event_preprocessor import EventPreprocessor
from src.preprocessing.graph_preprocessor import GraphPreprocessor
from src.preprocessing.label_processor import LabelProcessor
from src.models.input_schemas import EventInput, GraphInput, NodeInput, EdgeInput


class PreprocessingPipeline:
    """
    Orchestrates all preprocessing steps.
    
    Pipeline order:
    1. Data cleaning
    2. Event preprocessing
    3. Graph preprocessing
    4. Label processing
    5. Feature combination
    
    Example:
        pipeline = PreprocessingPipeline()
        result = pipeline.process(
            events=events,
            graph=graph,
            labels=labels,
            clean_data=True
        )
    """
    
    def __init__(self):
        """Initialize the preprocessing pipeline."""
        self.logger = get_logger("preprocessing.pipeline")
        
        # Initialize sub-processors
        self.data_cleaner = DataCleaner()
        self.event_preprocessor = EventPreprocessor()
        self.graph_preprocessor = GraphPreprocessor()
        self.label_processor = LabelProcessor()
        
        # Statistics tracking
        self._stats = {
            "events_processed": 0,
            "graphs_processed": 0,
            "labels_processed": 0,
            "features_generated": 0,
            "pipeline_complete": False,
            "started_at": None,
            "completed_at": None,
        }
        
        self._last_result = None
    
    def process(
        self,
        events: Optional[List[Dict[str, Any]]] = None,
        graph: Optional[GraphInput] = None,
        labels: Optional[List[Any]] = None,
        clean_data: bool = True,
        extract_features: bool = True,
        return_dataframe: bool = True,
    ) -> Dict[str, Any]:
        """
        Process data through the complete pipeline.
        
        Args:
            events: List of event dictionaries or EventInput objects
            graph: GraphInput object
            labels: List of labels (strings or integers)
            clean_data: Whether to clean data
            extract_features: Whether to extract features
            return_dataframe: Whether to return combined features as DataFrame
            
        Returns:
            Dict[str, Any]: Processed data with keys:
                - events: Cleaned events
                - event_features: Extracted event features
                - graph_data: Preprocessed graph data
                - labels: Original labels
                - encoded_labels: Encoded labels
                - label_mapping: Label to integer mapping
                - combined_features: Combined feature DataFrame
                - statistics: Processing statistics
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting preprocessing pipeline...")
        self._stats["started_at"] = datetime.utcnow()
        
        result = {
            "status": "processing",
            "statistics": {},
        }
        
        # ====================================================================
        # Step 1: Clean Events
        # ====================================================================
        if events:
            self.logger.info(f"Step 1: Cleaning {len(events)} events...")
            
            # Convert to dict if EventInput objects
            if events and hasattr(events[0], 'dict'):
                events = [e.dict() if hasattr(e, 'dict') else e for e in events]
            
            if clean_data:
                events = self.data_cleaner.clean_events(events)
            
            result["events"] = events
            self._stats["events_processed"] = len(events)
            self.logger.info(f"  → {len(events)} events after cleaning")
        
        # ====================================================================
        # Step 2: Preprocess Events (Extract Features)
        # ====================================================================
        if events and extract_features:
            self.logger.info("Step 2: Extracting event features...")
            
            try:
                event_features = self.event_preprocessor.preprocess(events)
                result["event_features"] = event_features
                self.logger.info(f"  → {len(event_features.columns)} features extracted")
            except Exception as e:
                self.logger.error(f"  → Event preprocessing failed: {e}")
                result["event_features"] = pd.DataFrame()
        
        # ====================================================================
        # Step 3: Preprocess Graph
        # ====================================================================
        if graph:
            self.logger.info(f"Step 3: Preprocessing graph ({len(graph.nodes)} nodes, {len(graph.edges)} edges)...")
            
            try:
                graph_data = self.graph_preprocessor.preprocess(graph)
                result["graph_data"] = graph_data
                self._stats["graphs_processed"] = 1
                
                self.logger.info(f"  → {len(graph_data['node_features'])} node features extracted")
                self.logger.info(f"  → {len(graph_data.get('edge_features', pd.DataFrame()))} edge features extracted")
                self.logger.info(f"  → Graph connected: {graph_data['statistics'].get('is_connected', False)}")
            except Exception as e:
                self.logger.error(f"  → Graph preprocessing failed: {e}")
                result["graph_data"] = {"node_features": pd.DataFrame(), "edge_features": pd.DataFrame()}
        
        # ====================================================================
        # Step 4: Process Labels
        # ====================================================================
        if labels:
            self.logger.info(f"Step 4: Processing {len(labels)} labels...")
            
            if clean_data:
                labels = self.data_cleaner.clean_labels(labels)
            
            # Create label mapping
            mapping = self.label_processor.create_mapping(labels)
            
            # Encode labels
            encoded_labels = self.label_processor.encode_labels(labels)
            
            # Validate labels
            is_valid = self.label_processor.validate_labels(labels)
            
            result["labels"] = labels
            result["encoded_labels"] = encoded_labels
            result["label_mapping"] = mapping
            result["label_distribution"] = self.label_processor.get_label_distribution(labels)
            result["labels_valid"] = is_valid
            
            self._stats["labels_processed"] = len(labels)
            self.logger.info(f"  → {len(mapping)} classes found")
            self.logger.info(f"  → Labels valid: {is_valid}")
            self.logger.info(f"  → Distribution: {result['label_distribution']}")
        
        # ====================================================================
        # Step 5: Combine Features
        # ====================================================================
        self.logger.info("Step 5: Combining features...")
        result = self._combine_features(result, return_dataframe)
        
        # ====================================================================
        # Step 6: Generate Statistics
        # ====================================================================
        self._stats["completed_at"] = datetime.utcnow()
        self._stats["pipeline_complete"] = True
        
        duration = (self._stats["completed_at"] - self._stats["started_at"]).total_seconds()
        
        result["statistics"] = {
            "pipeline": self._stats.copy(),
            "data_cleaner": self.data_cleaner.get_statistics(),
            "event_preprocessor": self.event_preprocessor.get_statistics(),
            "graph_preprocessor": self.graph_preprocessor.get_statistics(),
            "label_processor": self.label_processor.get_statistics(),
            "duration_seconds": duration,
        }
        
        result["status"] = "completed"
        self._last_result = result
        
        self.logger.info("=" * 60)
        self.logger.info(f"Preprocessing pipeline complete! (Duration: {duration:.2f}s)")
        self.logger.info("=" * 60)
        
        return result
    
    def _combine_features(self, data: Dict[str, Any], return_dataframe: bool = True) -> Dict[str, Any]:
        """
        Combine all features into a single dataset.
        
        Args:
            data: Current result data
            return_dataframe: Whether to return as DataFrame
            
        Returns:
            Dict[str, Any]: Updated data with combined features
        """
        combined_features = None
        
        # Start with event features
        if "event_features" in data and not data["event_features"].empty:
            combined_features = data["event_features"].copy()
            self.logger.info(f"  → Starting with event features: {combined_features.shape}")
        
        # Add graph node features
        if "graph_data" in data:
            graph_data = data["graph_data"]
            
            if "node_features" in graph_data and not graph_data["node_features"].empty:
                node_features = graph_data["node_features"].copy()
                
                if combined_features is not None:
                    # Try to merge on node_id
                    if "node_id" in combined_features.columns and "node_id" in node_features.columns:
                        # Check if we have matching node_ids
                        common_ids = set(combined_features['node_id']) & set(node_features['node_id'])
                        
                        if len(common_ids) > 0:
                            combined_features = combined_features.merge(
                                node_features,
                                on="node_id",
                                how="outer",
                                suffixes=('', '_graph')
                            )
                            self.logger.info(f"  → Merged with graph features: {combined_features.shape}")
                        else:
                            self.logger.warning("  → No common node_ids found, concatenating features")
                            # Concatenate if no common IDs
                            combined_features = pd.concat([combined_features, node_features], axis=1)
                    else:
                        # Concatenate if no node_id columns
                        combined_features = pd.concat([combined_features, node_features], axis=1)
                        self.logger.info(f"  → Concatenated with graph features: {combined_features.shape}")
                else:
                    combined_features = node_features
                    self.logger.info(f"  → Using graph features only: {combined_features.shape}")
        
        # Add labels
        if "encoded_labels" in data and combined_features is not None:
            labels = data["encoded_labels"]
            
            # Ensure labels length matches features
            if len(labels) == len(combined_features):
                combined_features['label'] = labels
                self.logger.info(f"  → Added labels column")
            else:
                self.logger.warning(
                    f"  → Label length ({len(labels)}) doesn't match features ({len(combined_features)})"
                )
        
        # Add to result
        if combined_features is not None:
            if return_dataframe:
                data["combined_features"] = combined_features
            else:
                data["combined_features"] = combined_features.to_dict('records')
            
            self._stats["features_generated"] = len(combined_features.columns)
            self.logger.info(f"  → Final combined features: {combined_features.shape}")
        else:
            self.logger.warning("  → No features to combine")
            data["combined_features"] = pd.DataFrame() if return_dataframe else []
        
        return data
    
    def process_cicids_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process a CICIDS DataFrame through the pipeline.
        
        Args:
            df: Input DataFrame (must have 'Label' column)
            
        Returns:
            pd.DataFrame: Processed DataFrame with features and labels
        """
        self.logger.info(f"Processing CICIDS DataFrame with {len(df)} rows")
        
        # Separate features and labels
        if 'Label' in df.columns:
            labels = df['Label'].tolist()
            features = df.drop('Label', axis=1)
        else:
            labels = None
            features = df
        
        # Clean data
        features = self.data_cleaner.clean_dataframe(features)
        
        # Process labels
        if labels is not None:
            self.label_processor.create_mapping(labels)
            encoded = self.label_processor.encode_labels(labels)
            features['label'] = encoded
            
            # Add label distribution info
            self.logger.info(f"Label distribution: {self.label_processor.get_label_distribution(labels)}")
        
        self.logger.info(f"Processed DataFrame: {features.shape}")
        return features
    
    def process_batch(
        self,
        items: List[Dict[str, Any]],
        batch_size: int = 100,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of items through the pipeline.
        
        Args:
            items: List of items to process
            batch_size: Size of each batch
            **kwargs: Additional arguments for process()
            
        Returns:
            List[Dict[str, Any]]: Processed results
        """
        self.logger.info(f"Processing batch of {len(items)} items (batch_size={batch_size})")
        
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1}")
            
            result = self.process(events=batch, **kwargs)
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.
        
        Returns:
            Dict[str, Any]: Combined statistics
        """
        return {
            "pipeline": self._stats.copy(),
            "data_cleaner": self.data_cleaner.get_statistics(),
            "event_preprocessor": self.event_preprocessor.get_statistics(),
            "graph_preprocessor": self.graph_preprocessor.get_statistics(),
            "label_processor": self.label_processor.get_statistics(),
        }
    
    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the last processed result.
        
        Returns:
            Optional[Dict[str, Any]]: Last result or None
        """
        return self._last_result
    
    def reset(self) -> None:
        """Reset the pipeline state."""
        self._stats = {
            "events_processed": 0,
            "graphs_processed": 0,
            "labels_processed": 0,
            "features_generated": 0,
            "pipeline_complete": False,
            "started_at": None,
            "completed_at": None,
        }
        self._last_result = None
        self.logger.info("Pipeline reset")
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the last processing run.
        
        Returns:
            str: Summary string
        """
        if not self._last_result:
            return "No processing results available"
        
        stats = self._last_result.get("statistics", {})
        pipeline_stats = stats.get("pipeline", {})
        
        summary = [
            "=" * 60,
            "PREPROCESSING PIPELINE SUMMARY",
            "=" * 60,
            f"Status: {self._last_result.get('status', 'unknown')}",
            f"Duration: {stats.get('duration_seconds', 0):.2f}s",
            f"Events Processed: {pipeline_stats.get('events_processed', 0)}",
            f"Graphs Processed: {pipeline_stats.get('graphs_processed', 0)}",
            f"Labels Processed: {pipeline_stats.get('labels_processed', 0)}",
            f"Features Generated: {pipeline_stats.get('features_generated', 0)}",
        ]
        
        # Add label info
        if "label_distribution" in self._last_result:
            dist = self._last_result["label_distribution"]
            summary.append(f"Label Distribution: {dist}")
        
        # Add feature info
        if "combined_features" in self._last_result:
            cf = self._last_result["combined_features"]
            if isinstance(cf, pd.DataFrame):
                summary.append(f"Final Feature Shape: {cf.shape}")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)