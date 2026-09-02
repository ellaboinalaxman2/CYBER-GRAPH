"""Simple training script for GraphSAGE model (without scipy dependency)."""

import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.logging import setup_logging, get_logger


class SimpleGraphSAGE(nn.Module):
    """Simple GraphSAGE model for testing."""
    
    def __init__(self, in_channels, hidden_channels, out_channels, num_layers=3):
        super().__init__()
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(in_channels, hidden_channels))
        
        # Hidden layers
        for _ in range(num_layers - 1):
            self.layers.append(nn.Linear(hidden_channels, hidden_channels))
        
        # Output layer
        self.layers.append(nn.Linear(hidden_channels, out_channels))
        
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x, edge_index=None):
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x)
            x = F.relu(x)
            x = self.dropout(x)
        
        x = self.layers[-1](x)
        return x
    
    def predict(self, x, edge_index=None):
        logits = self.forward(x, edge_index)
        return logits.argmax(dim=1)
    
    def predict_proba(self, x, edge_index=None):
        logits = self.forward(x, edge_index)
        return F.softmax(logits, dim=1)
    
    def count_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def generate_sample_data(num_nodes=100, num_features=16, num_classes=2):
    """Generate sample data for training."""
    # Features
    x = torch.randn(num_nodes, num_features)
    
    # Random edges (sparse)
    num_edges = num_nodes * 3
    edge_index = torch.randint(0, num_nodes, (2, num_edges))
    
    # Labels (with some class imbalance)
    y = torch.randint(0, num_classes, (num_nodes,))
    
    # Split into train/val/test
    perm = torch.randperm(num_nodes)
    train_size = int(0.7 * num_nodes)
    val_size = int(0.15 * num_nodes)
    
    train_idx = perm[:train_size]
    val_idx = perm[train_size:train_size + val_size]
    test_idx = perm[train_size + val_size:]
    
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)
    
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True
    
    return {
        'x': x,
        'edge_index': edge_index,
        'y': y,
        'train_mask': train_mask,
        'val_mask': val_mask,
        'test_mask': test_mask,
    }


def train_model(data, epochs=100, lr=0.001, device='cpu'):
    """Train the model."""
    logger = get_logger("scripts.train_simple")
    
    # Move data to device
    x = data['x'].to(device)
    edge_index = data['edge_index'].to(device)
    y = data['y'].to(device)
    train_mask = data['train_mask'].to(device)
    val_mask = data['val_mask'].to(device)
    
    # Create model
    model = SimpleGraphSAGE(
        in_channels=x.size(1),
        hidden_channels=64,
        out_channels=len(torch.unique(y)),
    )
    model.to(device)
    
    logger.info(f"Model has {model.count_parameters():,} parameters")
    
    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    # Training loop
    best_val_loss = float('inf')
    best_model_state = None
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        out = model(x, edge_index)
        loss = criterion(out[train_mask], y[train_mask])
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_out = model(x, edge_index)
            val_loss = criterion(val_out[val_mask], y[val_mask])
            
            # Accuracy
            pred = val_out[val_mask].argmax(dim=1)
            val_acc = (pred == y[val_mask]).float().mean()
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict().copy()
        
        if epoch % 10 == 0:
            logger.info(f"Epoch {epoch}: Loss={loss.item():.4f}, Val Loss={val_loss.item():.4f}, Val Acc={val_acc.item():.4f}")
    
    # Load best model
    model.load_state_dict(best_model_state)
    
    # Test
    model.eval()
    with torch.no_grad():
        test_out = model(x, edge_index)
        pred = test_out[data['test_mask']].argmax(dim=1)
        test_acc = (pred == y[data['test_mask']]).float().mean()
    
    logger.info(f"Test Accuracy: {test_acc.item():.4f}")
    
    return {
        'model': model,
        'test_accuracy': test_acc.item(),
        'best_val_loss': best_val_loss,
        'history': {'train_loss': [], 'val_loss': []},
    }


def main():
    """Main function."""
    setup_logging()
    logger = get_logger("scripts.train_simple")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Using device: {device}")
    
    # Generate sample data
    logger.info("Generating sample data...")
    data = generate_sample_data(num_nodes=200, num_features=16, num_classes=2)
    
    # Train model
    logger.info("Training model...")
    results = train_model(data, epochs=50, lr=0.001, device=device)
    
    # Save model
    save_dir = Path(settings.model_save_dir) / "production"
    save_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = save_dir / "simple_graphsage.pt"
    torch.save({
        'model_state_dict': results['model'].state_dict(),
        'config': {
            'in_channels': 16,
            'hidden_channels': 64,
            'out_channels': 2,
        },
        'test_accuracy': results['test_accuracy'],
    }, model_path)
    
    logger.info(f"Model saved to {model_path}")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Test Accuracy: {results['test_accuracy']:.4f}")
    print(f"Best Validation Loss: {results['best_val_loss']:.4f}")
    print(f"Model saved to: {model_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()