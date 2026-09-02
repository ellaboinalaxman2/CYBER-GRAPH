"""Severity calculation for Member 5 - Attack Engine."""

from typing import Dict, Any, Optional
from enum import Enum


class SeverityLevel(str, Enum):
    """Severity levels."""
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SeverityCalculator:
    """
    Calculates severity from risk scores.
    
    Features:
    - Map risk score to severity
    - Get severity thresholds
    - Custom thresholds
    """
    
    def __init__(self):
        """Initialize the severity calculator."""
        self.thresholds = {
            SeverityLevel.LOW: 0,
            SeverityLevel.MEDIUM: 25,
            SeverityLevel.HIGH: 50,
            SeverityLevel.CRITICAL: 75,
        }
    
    def calculate(self, risk_score: float) -> SeverityLevel:
        """
        Calculate severity from risk score.
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            SeverityLevel: Severity level
        """
        if risk_score >= self.thresholds[SeverityLevel.CRITICAL]:
            return SeverityLevel.CRITICAL
        elif risk_score >= self.thresholds[SeverityLevel.HIGH]:
            return SeverityLevel.HIGH
        elif risk_score >= self.thresholds[SeverityLevel.MEDIUM]:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def get_threshold(self, severity: SeverityLevel) -> int:
        """
        Get threshold for a severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            int: Threshold value
        """
        return self.thresholds.get(severity, 0)
    
    def set_threshold(self, severity: SeverityLevel, threshold: int) -> None:
        """
        Set threshold for a severity level.
        
        Args:
            severity: Severity level
            threshold: Threshold value (0-100)
        """
        if 0 <= threshold <= 100:
            self.thresholds[severity] = threshold
        else:
            raise ValueError("Threshold must be between 0 and 100")
    
    def get_severity_color(self, severity: SeverityLevel) -> str:
        """
        Get color for a severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            str: Hex color code
        """
        colors = {
            SeverityLevel.LOW: "#2ecc71",      # Green
            SeverityLevel.MEDIUM: "#f39c12",    # Yellow
            SeverityLevel.HIGH: "#e67e22",      # Orange
            SeverityLevel.CRITICAL: "#e74c3c",   # Red
        }
        return colors.get(severity, "#95a5a6")
    
    def get_severity_icon(self, severity: SeverityLevel) -> str:
        """
        Get icon for a severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            str: Icon
        """
        icons = {
            SeverityLevel.LOW: "ℹ️",
            SeverityLevel.MEDIUM: "⚠️",
            SeverityLevel.HIGH: "🔴",
            SeverityLevel.CRITICAL: "🚨",
        }
        return icons.get(severity, "❓")