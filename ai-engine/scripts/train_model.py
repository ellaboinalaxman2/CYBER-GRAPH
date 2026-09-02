"""Training script for GraphSAGE model."""

import sys
import argparse
from pathlib import Path
import torch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.data import DatasetLoader
from src.preprocessing import PreprocessingPipeline
from src.features import FeatureBuilder
from src.graph import GraphBuilder, GraphConverter, GraphSampler
from src.training import GraphSAGETrainer, TrainingConfig


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train GraphSAGE model")
    parser.add_argument(
        "--dataset",
        type=str,
        default="sample",
        help="Dataset to use (sample, cicids)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save trained model"
    )
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = get_logger("scripts.train_model")
    
    logger.info("Starting GraphSAGE training...")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Learning Rate: {args.lr}")
    logger.info(f"Device: {args.device}")
    
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
    # Create Train/Val/Test Masks
    # ========================================================================
    num_nodes = data_torch.num_nodes
    num_train = int(num_nodes * 0.7)
    num_val = int(num_nodes * 0.15)
    
    # Random permutation
    idx = torch.randperm(num_nodes)
    train_idx = idx[:num_train]
    val_idx = idx[num_train:num_train + num_val]
    test_idx = idx[num_train + num_val:]
    
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)
    
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True
    
    # ========================================================================
    # Train Model
    # ========================================================================
    logger.info("Training GraphSAGE model...")
    
    trainer = GraphSAGETrainer(config={
        'in_channels': data_torch.x.size(1),
        'num_classes': len(torch.unique(data_torch.y)),
        'max_epochs': args.epochs,
        'learning_rate': args.lr,
        'device': args.device,
    })
    
    results = trainer.train(
        data=data_torch,
        train_mask=train_mask,
        val_mask=val_mask,
        test_mask=test_mask,
    )
    
    # ========================================================================
    # Save Model
    # ========================================================================
    if args.save:
        logger.info("Saving model...")
        save_path = Path(settings.model_save_dir) / "production"
        save_path.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'model_state_dict': trainer.model.state_dict(),
            'config': trainer.config,
            'results': results,
            'history': trainer.trainer.training_history,
        }
        
        torch.save(checkpoint, save_path / "graphsage_model.pt")
        logger.info(f"Model saved to {save_path / 'graphsage_model.pt'}")
    
    # ========================================================================
    # Print Results
    # ========================================================================
    print("\n" + "=" * 60)
    print("TRAINING RESULTS")
    print("=" * 60)
    print(f"Best Loss: {results.get('best_loss', 'N/A')}")
    print(f"Best Epoch: {results.get('best_epoch', 'N/A')}")
    print(f"Test Loss: {results.get('test_loss', 'N/A')}")
    
    if 'test_metrics' in results:
        print("\nTest Metrics:")
        for key, value in results['test_metrics'].items():
            print(f"  {key}: {value:.4f}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()