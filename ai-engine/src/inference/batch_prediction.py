"""Batch prediction for Member 3 - AI Engine."""

import torch
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from src.core.logging import get_logger
from src.core.exceptions import InferenceError
from src.inference.predictor import Predictor, PredictionResult


class BatchPredictor:
    """
    Batch prediction for multiple nodes.
    
    Features:
    - Parallel prediction
    - Progress tracking
    - Result aggregation
    - Summary statistics
    """
    
    def __init__(
        self,
        predictor: Predictor,
        max_workers: int = 4,
        show_progress: bool = True,
    ):
        """
        Initialize the batch predictor.
        
        Args:
            predictor: Predictor instance
            max_workers: Maximum parallel workers
            show_progress: Whether to show progress bar
        """
        self.logger = get_logger("inference.batch_predictor")
        self.predictor = predictor
        self.max_workers = max_workers
        self.show_progress = show_progress
        self._stats = {
            "total_batches": 0,
            "total_predictions": 0,
            "avg_time_per_prediction": 0.0,
        }
    
    def predict_batch(
        self,
        node_data_list: List[Dict[str, Any]],
        graph_data: Optional[Dict[str, Any]] = None,
        parallel: bool = False,
    ) -> List[PredictionResult]:
        """
        Predict for multiple nodes.
        
        Args:
            node_data_list: List of node data
            graph_data: Graph data (optional)
            parallel: Whether to run in parallel
            
        Returns:
            List[PredictionResult]: Prediction results
        """
        self.logger.info(f"Predicting for {len(node_data_list)} nodes")
        
        if parallel:
            results = self._predict_parallel(node_data_list, graph_data)
        else:
            results = self._predict_sequential(node_data_list, graph_data)
        
        # Update stats
        self._stats["total_batches"] += 1
        self._stats["total_predictions"] += len(results)
        
        return results
    
    def _predict_sequential(
        self,
        node_data_list: List[Dict[str, Any]],
        graph_data: Optional[Dict[str, Any]] = None,
    ) -> List[PredictionResult]:
        """Predict sequentially."""
        results = []
        iterator = tqdm(node_data_list, desc="Predicting") if self.show_progress else node_data_list
        
        for node_data in iterator:
            result = self.predictor.predict(node_data, graph_data)
            results.append(result)
        
        return results
    
    def _predict_parallel(
        self,
        node_data_list: List[Dict[str, Any]],
        graph_data: Optional[Dict[str, Any]] = None,
    ) -> List[PredictionResult]:
        """Predict in parallel."""
        results = []
        
        def predict_single(node_data):
            return self.predictor.predict(node_data, graph_data)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = [
                executor.submit(predict_single, node_data)
                for node_data in node_data_list
            ]
            
            # Collect results
            iterator = tqdm(futures, desc="Predicting") if self.show_progress else futures
            for future in iterator:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Prediction failed: {e}")
        
        return results
    
    def predict_batch_with_summary(
        self,
        node_data_list: List[Dict[str, Any]],
        graph_data: Optional[Dict[str, Any]] = None,
        parallel: bool = False,
    ) -> Dict[str, Any]:
        """
        Predict and return with summary.
        
        Args:
            node_data_list: List of node data
            graph_data: Graph data (optional)
            parallel: Whether to run in parallel
            
        Returns:
            Dict[str, Any]: Results with summary
        """
        results = self.predict_batch(node_data_list, graph_data, parallel)
        
        # Generate summary
        summary = {
            "total_predictions": len(results),
            "normal_count": sum(1 for r in results if r.prediction == "NORMAL"),
            "attack_count": sum(1 for r in results if r.prediction == "ATTACK"),
            "avg_anomaly_score": np.mean([r.anomaly_score for r in results]),
            "max_anomaly_score": max([r.anomaly_score for r in results]),
            "min_anomaly_score": min([r.anomaly_score for r in results]),
            "avg_confidence": np.mean([r.confidence for r in results]),
        }
        
        # Node IDs with high anomaly scores
        high_risk = [
            {
                "node_id": r.node_id,
                "anomaly_score": r.anomaly_score,
                "prediction": r.prediction,
            }
            for r in results
            if r.anomaly_score > 0.7
        ]
        summary["high_risk_nodes"] = high_risk
        
        return {
            "results": [r.to_dict() for r in results],
            "summary": summary,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batch prediction statistics."""
        return self._stats.copy()