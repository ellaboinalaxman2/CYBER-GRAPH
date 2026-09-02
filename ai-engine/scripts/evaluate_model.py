"""Evaluation script for GraphSAGE model."""

import sys
import argparse
from pathlib import Path
import torch
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.data import DatasetLoader
from src.preprocessing import PreprocessingPipeline
from src.features import FeatureBuilder
from src.graph import GraphBuilder, GraphConverter
from src.models import ModelFactory
from src.evaluation import Evaluator, EvaluationConfig


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate GraphSAGE model")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to trained model checkpoint"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="sample",
        help="Dataset to use (sample, cicids)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./data/models/evaluation",
        help="Output directory for results"
    )
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = get_logger("scripts.evaluate_model")
    
    logger.info("Starting model evaluation...")
    logger.info(f"Model: {args.model_path}")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Device: {args.device}")
    
    # ========================================================================
    # Load Model
    # ========================================================================
    logger.info("Loading model...")
    
    checkpoint = torch.load(args.model_path, map_location=args.device)
    
    # Create model
    model_config = checkpoint.get('config', {})
    model = ModelFactory.create_default_classifier(
        in_channels=model_config.get('in_channels', 128),
        num_classes=model_config.get('num_classes', 2),
        hidden_channels=model_config.get('hidden_channels', 128),
        num_layers=model_config.get('num_layers', 3),
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(args.device)
    model.eval()
    
    logger.info("Model loaded successfully")
    
    # ========================================================================
    # Load Data
    # ========================================================================
    logger.info("Loading dataset...")
    
    loader = DatasetLoader()
    data = loader.load_dataset(args.dataset, sample_size=500)
    
    # ========================================================================
    # Preprocess Data
    # ========================================================================
    logger.info("Preprocessing data...")
    
    pipeline = PreprocessingPipeline()
    processed = pipeline.process(
        events=data.get("events"),
        graph=data.get("graph"),
        labels=data.get("labels"),
        clean_data=True,
    )
    
    # ========================================================================
    # Build Features
    # ========================================================================
    logger.info("Building features...")
    
    builder = FeatureBuilder()
    features = builder.build_features(
        nodes=processed.get("graph", {}).get("nodes", []),
        edges=processed.get("graph", {}).get("edges", []),
        events=processed.get("events", []),
        normalize=True,
    )
    
    # ========================================================================
    # Build Graph
    # ========================================================================
    logger.info("Building ML graph...")
    
    graph_builder = GraphBuilder()
    ml_graph = graph_builder.build_graph(
        nodes=processed.get("graph", {}).get("nodes", []),
        edges=processed.get("graph", {}).get("edges", []),
        labels=processed.get("encoded_labels"),
    )
    
    # ========================================================================
    # Convert to PyTorch Geometric
    # ========================================================================
    logger.info("Converting graph...")
    
    converter = GraphConverter(device=args.device)
    data_torch = converter.convert(ml_graph)
    
    # ========================================================================
    # Evaluate
    # ========================================================================
    logger.info("Evaluating model...")
    
    eval_config = EvaluationConfig(
        plot_confusion_matrix=True,
        plot_roc=True,
        plot_pr=True,
        save_results=True,
        output_dir=args.output_dir,
    )
    
    evaluator = Evaluator(config=eval_config)
    
    # Prepare evaluation data
    eval_data = {
        'x': data_torch.x,
        'edge_index': data_torch.edge_index,
        'y': data_torch.y,
    }
    
    # Evaluate
    results = evaluator.evaluate(
        model=model,
        data=eval_data,
        name=Path(args.model_path).stem,
        labels=['Normal', 'Attack'],
    )
    
    # ========================================================================
    # Print Results
    # ========================================================================
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    
    metrics = results['metrics']
    print(f"Accuracy: {metrics.get('accuracy', 0):.4f}")
    print(f"Precision: {metrics.get('precision', 0):.4f}")
    print(f"Recall: {metrics.get('recall', 0):.4f}")
    print(f"F1 Score: {metrics.get('f1', 0):.4f}")
    
    if 'roc_auc' in metrics:
        print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    if 'pr_auc' in metrics:
        print(f"PR-AUC: {metrics['pr_auc']:.4f}")
    
    print("\nConfusion Matrix:")
    print(results['confusion_matrix'])
    
    print("\n" + "=" * 60)
    print(f"Results saved to: {args.output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()