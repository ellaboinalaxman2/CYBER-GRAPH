"""Data cleaner for handling missing values, duplicates, and invalid data."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from src.core.logging import get_logger
from src.core.exceptions import PreprocessingError


class DataCleaner:
    """
    Cleans raw data for ML processing.
    
    Handles:
    - Missing values
    - Duplicate records
    - Invalid values
    - Inconsistent formats
    - Outliers
    """
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.logger = get_logger("preprocessing.data_cleaner")
        self._stats = {
            "total_rows": 0,
            "rows_removed": 0,
            "rows_modified": 0,
            "missing_values_filled": 0,
            "duplicates_removed": 0,
            "outliers_handled": 0,
        }
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a pandas DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        self.logger.info(f"Cleaning DataFrame with {len(df)} rows")
        self._stats["total_rows"] = len(df)
        
        df = df.copy()
        
        # Step 1: Remove duplicates
        df = self._remove_duplicates(df)
        
        # Step 2: Handle missing values
        df = self._handle_missing_values(df)
        
        # Step 3: Fix invalid values
        df = self._fix_invalid_values(df)
        
        # Step 4: Handle outliers
        df = self._handle_outliers(df)
        
        # Step 5: Standardize formats
        df = self._standardize_formats(df)
        
        self.logger.info(f"Cleaned DataFrame: {len(df)} rows remaining")
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows."""
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        
        removed = before - after
        self._stats["duplicates_removed"] = removed
        self._stats["rows_removed"] += removed
        
        if removed > 0:
            self.logger.info(f"Removed {removed} duplicate rows")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in DataFrame."""
        missing_before = df.isnull().sum().sum()
        
        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                self._stats["missing_values_filled"] += df[col].isnull().sum()
        
        # Fill categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().any():
                mode_val = df[col].mode()[0] if not df[col].mode().empty else 'unknown'
                df[col].fillna(mode_val, inplace=True)
                self._stats["missing_values_filled"] += df[col].isnull().sum()
        
        # Remove rows with any remaining missing values
        before = len(df)
        df = df.dropna()
        after = len(df)
        
        missing_after = df.isnull().sum().sum()
        self._stats["rows_removed"] += before - after
        
        self.logger.info(
            f"Missing values: {missing_before} → {missing_after} "
            f"(filled: {self._stats['missing_values_filled']})"
        )
        
        return df
    
    def _fix_invalid_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix invalid values in DataFrame."""
        # Fix negative values in count columns
        count_cols = [col for col in df.columns if 'count' in col.lower() or 'packets' in col.lower()]
        for col in count_cols:
            if col in df.columns and df[col].dtype in ['int64', 'float64']:
                invalid = (df[col] < 0).sum()
                if invalid > 0:
                    df.loc[df[col] < 0, col] = 0
                    self._stats["rows_modified"] += invalid
        
        # Fix invalid ports (0-65535)
        port_cols = [col for col in df.columns if 'port' in col.lower()]
        for col in port_cols:
            if col in df.columns:
                invalid = ((df[col] < 0) | (df[col] > 65535)).sum()
                if invalid > 0:
                    df.loc[df[col] < 0, col] = 0
                    df.loc[df[col] > 65535, col] = 65535
                    self._stats["rows_modified"] += invalid
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """Handle outliers using IQR method."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if df[col].nunique() > 2:  # Skip binary columns
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                
                if outliers > 0:
                    # Cap outliers at bounds
                    df.loc[df[col] < lower_bound, col] = lower_bound
                    df.loc[df[col] > upper_bound, col] = upper_bound
                    self._stats["outliers_handled"] += outliers
                    self._stats["rows_modified"] += outliers
        
        if self._stats["outliers_handled"] > 0:
            self.logger.info(f"Handled {self._stats['outliers_handled']} outliers")
        
        return df
    
    def _standardize_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize formats in DataFrame."""
        # String columns: strip whitespace and convert to lowercase
        string_cols = df.select_dtypes(include=['object']).columns
        for col in string_cols:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        # Date columns: convert to datetime
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower() or 'timestamp' in col.lower()]
        for col in date_cols:
            if col in df.columns and df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], utc=True)
                except:
                    self.logger.warning(f"Could not convert {col} to datetime")
        
        return df
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cleaning statistics."""
        return self._stats.copy()
    
    def clean_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean a list of event dictionaries.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List[Dict[str, Any]]: Cleaned events
        """
        if not events:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        
        # Clean
        cleaned_df = self.clean_dataframe(df)
        
        # Convert back to dict
        return cleaned_df.to_dict('records')
    
    def clean_labels(self, labels: List[Any]) -> List[Any]:
        """
        Clean labels.
        
        Args:
            labels: List of labels
            
        Returns:
            List[Any]: Cleaned labels
        """
        # Remove empty labels
        labels = [l for l in labels if l is not None and str(l).strip()]
        
        # Standardize string labels
        labels = [str(l).strip().upper() if isinstance(l, str) else l for l in labels]
        
        return labels