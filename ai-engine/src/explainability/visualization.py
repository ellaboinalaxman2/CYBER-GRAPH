"""Explanation visualization for Member 3 - AI Engine."""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import seaborn as sns
from io import BytesIO
import base64

from src.core.logging import get_logger


class ExplanationVisualizer:
    """
    Visualizes explanations for predictions.
    
    Features:
    - Feature importance bar chart
    - Node explanation dashboard
    - Network visualization
    - Confidence visualization
    """
    
    def __init__(self):
        """Initialize the explanation visualizer."""
        self.logger = get_logger("explainability.visualization")
        self._stats = {
            "total_visualizations": 0,
        }
    
    def plot_feature_importance(
        self,
        feature_importance: Dict[str, float],
        title: str = "Feature Importance",
        top_k: int = 10,
        figsize: Tuple[int, int] = (10, 6),
        save_path: Optional[str] = None,
        return_base64: bool = False,
    ) -> Optional[str]:
        """
        Plot feature importance bar chart.
        
        Args:
            feature_importance: Feature importance scores
            title: Plot title
            top_k: Number of top features to show
            figsize: Figure size
            save_path: Path to save figure
            return_base64: Whether to return base64 encoded image
            
        Returns:
            Optional[str]: Base64 encoded image if requested
        """
        # Sort by importance
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        if not sorted_features:
            self.logger.warning("No features to plot")
            return None
        
        features, scores = zip(*sorted_features)
        
        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(features)))
        bars = ax.barh(features, scores, color=colors)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            ax.text(
                score + 0.01,
                bar.get_y() + bar.get_height() / 2,
                f'{score:.2%}',
                va='center',
                fontsize=10,
            )
        
        ax.set_xlabel('Importance')
        ax.set_title(title)
        ax.set_xlim(0, max(scores) * 1.15 if scores else 1)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        self._stats["total_visualizations"] += 1
        
        return self._save_or_encode(fig, save_path, return_base64)
    
    def plot_explanation_dashboard(
        self,
        node_id: str,
        prediction: str,
        confidence: float,
        anomaly_score: float,
        feature_importance: Dict[str, float],
        reasons: List[str],
        recommendations: List[str],
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None,
        return_base64: bool = False,
    ) -> Optional[str]:
        """
        Plot explanation dashboard.
        
        Args:
            node_id: Node identifier
            prediction: Predicted class
            confidence: Prediction confidence
            anomaly_score: Anomaly score
            feature_importance: Feature importance scores
            reasons: List of reasons
            recommendations: List of recommendations
            figsize: Figure size
            save_path: Path to save figure
            return_base64: Whether to return base64 encoded image
            
        Returns:
            Optional[str]: Base64 encoded image if requested
        """
        fig = plt.figure(figsize=figsize)
        
        # Create subplot grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Title
        fig.suptitle(f'Explanation Dashboard - Node: {node_id}', fontsize=16, fontweight='bold')
        
        # 1. Prediction summary (top-left)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.axis('off')
        
        color = '#2ecc71' if prediction == "NORMAL" else '#e74c3c'
        status_text = f'Status: {prediction}'
        ax1.text(0.5, 0.7, status_text, fontsize=14, fontweight='bold', 
                color=color, ha='center', va='center')
        
        # Confidence and anomaly score
        ax1.text(0.5, 0.4, f'Confidence: {confidence:.1%}', 
                fontsize=12, ha='center', va='center')
        ax1.text(0.5, 0.2, f'Anomaly Score: {anomaly_score:.1%}', 
                fontsize=12, ha='center', va='center')
        
        # 2. Feature importance (top-middle)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_mini_feature_importance(ax2, feature_importance)
        
        # 3. Reasons (top-right)
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.axis('off')
        ax3.text(0.05, 0.95, 'Key Reasons:', fontsize=12, fontweight='bold', va='top')
        
        for i, reason in enumerate(reasons[:5]):
            y_pos = 0.85 - (i * 0.12)
            if y_pos > 0:
                ax3.text(0.05, y_pos, f'• {reason}', fontsize=10, va='top', wrap=True)
        
        # 4. Recommendations (bottom row, spanning all columns)
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')
        ax4.text(0.05, 0.95, 'Recommendations:', fontsize=12, fontweight='bold', va='top')
        
        for i, recommendation in enumerate(recommendations[:3]):
            y_pos = 0.8 - (i * 0.15)
            if y_pos > 0:
                ax4.text(0.05, y_pos, f'• {recommendation}', fontsize=10, va='top', wrap=True)
        
        plt.tight_layout()
        
        self._stats["total_visualizations"] += 1
        
        return self._save_or_encode(fig, save_path, return_base64)
    
    def _plot_mini_feature_importance(self, ax, feature_importance: Dict[str, float]):
        """Plot mini feature importance."""
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        if not sorted_features:
            ax.axis('off')
            return
        
        features, scores = zip(*sorted_features)
        
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(features)))
        bars = ax.barh(features, scores, color=colors)
        
        ax.set_title('Top Features', fontsize=10)
        ax.set_xlim(0, max(scores) * 1.1 if scores else 1)
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.3, axis='x')
    
    def _save_or_encode(
        self,
        fig: plt.Figure,
        save_path: Optional[str] = None,
        return_base64: bool = False,
    ) -> Optional[str]:
        """
        Save figure or encode as base64.
        
        Args:
            fig: Matplotlib figure
            save_path: Path to save figure
            return_base64: Whether to return base64 encoded image
            
        Returns:
            Optional[str]: Base64 encoded image if requested
        """
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved visualization to {save_path}")
        
        if return_base64:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close(fig)
            return image_base64
        
        plt.close(fig)
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get visualization statistics."""
        return self._stats.copy()