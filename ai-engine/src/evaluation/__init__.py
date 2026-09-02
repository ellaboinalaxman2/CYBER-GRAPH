"""Evaluation module for Member 3 - AI Engine."""

from src.evaluation.evaluator import Evaluator, EvaluationConfig
from src.evaluation.metrics import MetricsCalculator
from src.evaluation.confusion_matrix import ConfusionMatrix
from src.evaluation.roc_curve import ROCCurve
from src.evaluation.model_comparison import ModelComparison

__all__ = [
    "Evaluator",
    "EvaluationConfig",
    "MetricsCalculator",
    "ConfusionMatrix",
    "ROCCurve",
    "ModelComparison",
]