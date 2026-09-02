"""Feature normalizer for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

from src.core.logging import get_logger
from src.core.exceptions import FeatureEngineeringError


class FeatureNormalizer:
    """
    Normalizes features for ML training.
    
    Methods:
    - Standard scaling (z-score)
    - Min-max scaling (0-1)
    - Robust scaling (percentile-based)
    """
    
    def __init__(self, method: str = 'standard'):
        """
        Initialize the normalizer.
        
        Args:
            method: Normalization method ('standard', 'minmax', 'robust')
        """
        self.logger = get_logger("features.feature_normalizer")
        self.method = method
        self._scaler = None
        self._params = {}
        self._stats = {
            "features_normalized": 0,
            "method": method,
            "columns_normalized": 0,
        }
    
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize features.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: Normalized DataFrame
        """
        if df.empty:
            return df
        
        self.logger.info(f"Normalizing {len(df.columns)} features using {self.method}")
        
        # Separate numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Normalize numeric columns
        if numeric_cols:
            normalized_numeric = self._normalize_numeric(df[numeric_cols])
            df[numeric_cols] = normalized_numeric
        
        # Keep categorical columns as-is
        # (they should be one-hot encoded separately)
        
        self._stats["columns_normalized"] = len(numeric_cols)
        self._stats["features_normalized"] = len(df)
        
        self.logger.info(f"Normalized {len(numeric_cols)} numeric columns")
        return df
    
    def _normalize_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize numeric columns.
        
        Args:
            df: Numeric DataFrame
            
        Returns:
            pd.DataFrame: Normalized DataFrame
        """
        # Skip columns with constant values
        constant_cols = []
        for col in df.columns:
            if df[col].nunique() <= 1:
                constant_cols.append(col)
        
        if constant_cols:
            self.logger.info(f"Skipping {len(constant_cols)} constant columns")
        
        # Normalize
        if self.method == 'standard':
            return self._standard_scale(df)
        elif self.method == 'minmax':
            return self._minmax_scale(df)
        elif self.method == 'robust':
            return self._robust_scale(df)
        else:
            raise FeatureEngineeringError(f"Unknown normalization method: {self.method}")
    
    def _standard_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply standard scaling (z-score)."""
        scaler = StandardScaler()
        scaled = scaler.fit_transform(df)
        
        self._scaler = scaler
        self._params = {
            'mean': scaler.mean_.tolist() if hasattr(scaler, 'mean_') else None,
            'scale': scaler.scale_.tolist() if hasattr(scaler, 'scale_') else None,
        }
        
        return pd.DataFrame(scaled, columns=df.columns, index=df.index)
    
    def _minmax_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply min-max scaling (0-1)."""
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(df)
        
        self._scaler = scaler
        self._params = {
            'min': scaler.min_.tolist() if hasattr(scaler, 'min_') else None,
            'scale': scaler.scale_.tolist() if hasattr(scaler, 'scale_') else None,
        }
        
        return pd.DataFrame(scaled, columns=df.columns, index=df.index)
    
    def _robust_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply robust scaling (percentile-based)."""
        scaler = RobustScaler()
        scaled = scaler.fit_transform(df)
        
        self._scaler = scaler
        self._params = {
            'center': scaler.center_.tolist() if hasattr(scaler, 'center_') else None,
            'scale': scaler.scale_.tolist() if hasattr(scaler, 'scale_') else None,
        }
        
        return pd.DataFrame(scaled, columns=df.columns, index=df.index)
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted scaler.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: Transformed DataFrame
        """
        if self._scaler is None:
            raise FeatureEngineeringError("Scaler not fitted. Call normalize() first.")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            scaled = self._scaler.transform(df[numeric_cols])
            df[numeric_cols] = pd.DataFrame(scaled, columns=numeric_cols, index=df.index)
        
        return df
    
    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform normalized features.
        
        Args:
            df: Normalized DataFrame
            
        Returns:
            pd.DataFrame: Original-scale DataFrame
        """
        if self._scaler is None:
            raise FeatureEngineeringError("Scaler not fitted. Call normalize() first.")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            original = self._scaler.inverse_transform(df[numeric_cols])
            df[numeric_cols] = pd.DataFrame(original, columns=numeric_cols, index=df.index)
        
        return df
    
    def get_params(self) -> Dict[str, Any]:
        """Get normalization parameters."""
        return self._params.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get normalization statistics."""
        return self._stats.copy()