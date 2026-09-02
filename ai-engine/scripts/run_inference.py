"""Inference script for Member 3 - AI Engine."""

import sys
import json
import torch
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.inference import Predictor, BatchPredictor


def main():
    """Main inference function."""
    parser = argparse.ArgumentParser(description="Run inference with GraphSAGE")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to trained model checkpoint"
    )
    parser.add_argument(
        "--node_id",
        type=str,
        help="Single node ID to predict"
    )
    parser.add_argument(
        "--batch_file",
        type=str,
        help="JSON file with batch of nodes"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Device to use"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="inference_results.json",
        help="Output file for results"
    )
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = get_logger("scripts.run_inference")
    
    logger.info("Starting inference...")
    logger.info(f"Model: {args.model_path}")
    logger.info(f"Device: {args.device}")
    
    # Initialize predictor
    predictor = Predictor(model_path=args.model_path, device=args.device)
    batch_predictor = BatchPredictor(predictor)
    
    results = []
    
    if args.node_id:
        # Single node prediction
        logger.info(f"Predicting for node: {args.node_id}")
        
        node_data = {
            "node_id": args.node_id,
            "features": [],  # Will be filled from data
        }
        
        result = predictor.predict(node_data, return_embedding=True)
        results.append(result.to_dict())
        
        print("\n" + "=" * 60)
        print("PREDICTION RESULT")
        print("=" * 60)
        print(f"Node ID: {result.node_id}")
        print(f"Prediction: {result.prediction}")
        print(f"Probability: {result.probability:.4f}")
        print(f"Confidence: {result.confidence:.4f}")
        print(f"Anomaly Score: {result.anomaly_score:.4f}")
        print("=" * 60)
    
    elif args.batch_file:
        # Batch prediction
        logger.info(f"Batch prediction from: {args.batch_file}")
        
        with open(args.batch_file, 'r') as f:
            data = json.load(f)
        
        node_data_list = data.get("nodes", [])
        logger.info(f"Predicting for {len(node_data_list)} nodes")
        
        result = batch_predictor.predict_batch_with_summary(node_data_list)
        results = result["results"]
        
        print("\n" + "=" * 60)
        print("BATCH PREDICTION SUMMARY")
        print("=" * 60)
        summary = result["summary"]
        print(f"Total Predictions: {summary['total_predictions']}")
        print(f"Normal: {summary['normal_count']}")
        print(f"Attack: {summary['attack_count']}")
        print(f"Avg Anomaly Score: {summary['avg_anomaly_score']:.4f}")
        print(f"High Risk Nodes: {len(summary['high_risk_nodes'])}")
        print("=" * 60)
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            "results": results,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
        }, f, indent=2)
    
    logger.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()