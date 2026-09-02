"""Explanation script for Member 3 - AI Engine."""

import sys
import json
import torch
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.inference import Predictor
from src.explainability import PredictionExplanation, ExplanationVisualizer


def main():
    """Main explanation function."""
    parser = argparse.ArgumentParser(description="Explain a prediction")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to trained model checkpoint"
    )
    parser.add_argument(
        "--node_id",
        type=str,
        required=True,
        help="Node ID to explain"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Device to use"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualization"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="explanation_results.json",
        help="Output file for results"
    )
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = get_logger("scripts.explain_prediction")
    
    logger.info("Starting prediction explanation...")
    logger.info(f"Model: {args.model_path}")
    logger.info(f"Node: {args.node_id}")
    logger.info(f"Device: {args.device}")
    
    # Initialize components
    predictor = Predictor(model_path=args.model_path, device=args.device)
    explainer = PredictionExplanation()
    visualizer = ExplanationVisualizer()
    
    # Make prediction
    logger.info("Making prediction...")
    node_data = {"node_id": args.node_id}
    prediction_result = predictor.predict(node_data, return_embedding=True)
    
    logger.info(f"Prediction: {prediction_result.prediction}")
    logger.info(f"Confidence: {prediction_result.confidence:.4f}")
    logger.info(f"Anomaly Score: {prediction_result.anomaly_score:.4f}")
    
    # Generate explanation
    logger.info("Generating explanation...")
    explanation = explainer.explain(
        model=predictor.model,
        x=None,  # In real implementation, use actual features
        node_id=args.node_id,
        node_idx=0,
        edge_index=None,
        feature_names=None,
        neighbor_ids=None,
        prediction=prediction_result.prediction,
        confidence=prediction_result.confidence,
        anomaly_score=prediction_result.anomaly_score,
    )
    
    # Print results
    print("\n" + "=" * 60)
    print("PREDICTION EXPLANATION")
    print("=" * 60)
    print(f"Node ID: {args.node_id}")
    print(f"Prediction: {explanation.prediction}")
    print(f"Confidence: {explanation.confidence:.4f}")
    print(f"Anomaly Score: {explanation.anomaly_score:.4f}")
    print("\nSummary:")
    print(f"  {explanation.summary}")
    print("\nReasons:")
    for reason in explanation.detailed_reasons:
        print(f"  • {reason}")
    print("\nRecommendations:")
    for rec in explanation.recommendations:
        print(f"  • {rec}")
    print("=" * 60)
    
    # Generate visualization
    if args.visualize:
        logger.info("Generating visualization...")
        image_base64 = visualizer.plot_explanation_dashboard(
            node_id=args.node_id,
            prediction=explanation.prediction,
            confidence=explanation.confidence,
            anomaly_score=explanation.anomaly_score,
            feature_importance=explanation.feature_importance,
            reasons=explanation.detailed_reasons,
            recommendations=explanation.recommendations,
            save_path=f"explanation_{args.node_id}.png",
            return_base64=True,
        )
        print(f"\nVisualization saved to: explanation_{args.node_id}.png")
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            "node_id": args.node_id,
            "prediction": prediction_result.to_dict(),
            "explanation": explanation.to_dict(),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
        }, f, indent=2)
    
    logger.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()