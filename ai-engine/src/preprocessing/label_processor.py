"""Label processor for Member 3 - AI Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from collections import Counter

from src.core.logging import get_logger
from src.core.exceptions import PreprocessingError


class LabelProcessor:
    """
    Processes labels for ML training.
    
    Features:
    - Label encoding
    - Label mapping
    - Label balancing
    - Label validation
    """
    
    def __init__(self):
        """Initialize the label processor."""
        self.logger = get_logger("preprocessing.label_processor")
        self._label_mapping = {}
        self._inverse_mapping = {}
        self._stats = {
            "labels_processed": 0,
            "classes_found": 0,
            "mapping_created": False,
        }
    
    def create_mapping(self, labels: List[Any]) -> Dict[str, int]:
        """
        Create a label mapping from labels.
        
        Args:
            labels: List of labels
            
        Returns:
            Dict[str, int]: Label to integer mapping
        """
        unique_labels = sorted(set(str(l) for l in labels if l is not None))
        self._label_mapping = {label: idx for idx, label in enumerate(unique_labels)}
        self._inverse_mapping = {idx: label for label, idx in self._label_mapping.items()}
        
        self._stats["classes_found"] = len(unique_labels)
        self._stats["mapping_created"] = True
        
        self.logger.info(f"Created label mapping with {len(unique_labels)} classes")
        return self._label_mapping
    
    def encode_labels(self, labels: List[Any]) -> List[int]:
        """
        Encode labels to integers.
        
        Args:
            labels: List of labels
            
        Returns:
            List[int]: Encoded labels
        """
        if not self._label_mapping:
            self.create_mapping(labels)
        
        encoded = []
        for label in labels:
            if label is None:
                encoded.append(-1)
            else:
                encoded.append(self._label_mapping.get(str(label), -1))
        
        self._stats["labels_processed"] += len(encoded)
        return encoded
    
    def decode_labels(self, encoded: List[int]) -> List[Any]:
        """
        Decode integer labels back to original.
        
        Args:
            encoded: List of encoded labels
            
        Returns:
            List[Any]: Decoded labels
        """
        if not self._inverse_mapping:
            raise PreprocessingError("No label mapping found")
        
        return [self._inverse_mapping.get(e, None) for e in encoded]
    
    def balance_labels(
        self,
        labels: List[int],
        strategy: str = 'oversample'
    ) -> List[int]:
        """
        Balance labels using oversampling or undersampling.
        
        Args:
            labels: List of encoded labels
            strategy: 'oversample' or 'undersample'
            
        Returns:
            List[int]: Balanced labels
        """
        if not labels:
            return labels
        
        counter = Counter(labels)
        max_count = max(counter.values())
        min_count = min(counter.values())
        
        if strategy == 'oversample':
            # Oversample minority classes
            balanced = []
            for label, count in counter.items():
                if label == -1:  # Skip unknown
                    continue
                
                # Duplicate labels to reach max_count
                ratio = max_count // count
                if ratio > 1:
                    for _ in range(ratio - 1):
                        balanced.extend([label] * count)
                balanced.extend([label] * count)
            
            self.logger.info(f"Oversampled labels: {len(labels)} → {len(balanced)}")
            return balanced
            
        elif strategy == 'undersample':
            # Undersample majority classes
            balanced = []
            for label, count in counter.items():
                if label == -1:  # Skip unknown
                    continue
                
                sample_size = min(count, max_count // 2)
                sampled = [label] * sample_size
                balanced.extend(sampled)
            
            self.logger.info(f"Undersampled labels: {len(labels)} → {len(balanced)}")
            return balanced
        
        else:
            raise PreprocessingError(f"Unknown balancing strategy: {strategy}")
    
    def get_label_distribution(self, labels: List[Any]) -> Dict[str, int]:
        """
        Get the distribution of labels.
        
        Args:
            labels: List of labels
            
        Returns:
            Dict[str, int]: Label distribution
        """
        return dict(Counter(str(l) for l in labels if l is not None))
    
    def validate_labels(self, labels: List[Any]) -> bool:
        """
        Validate labels.
        
        Args:
            labels: List of labels
            
        Returns:
            bool: True if valid
        """
        if not labels:
            self.logger.warning("No labels provided")
            return False
        
        # Check for valid labels
        valid_labels = [l for l in labels if l is not None]
        
        if not valid_labels:
            self.logger.warning("No valid labels found")
            return False
        
        # Check class balance
        distribution = self.get_label_distribution(valid_labels)
        
        if len(distribution) < 2:
            self.logger.warning(f"Only one class found: {distribution}")
            return False
        
        self.logger.info(f"Label validation passed: {len(distribution)} classes found")
        return True
    
    def map_to_binary(self, labels: List[Any], positive_class: Optional[str] = None) -> List[int]:
        """
        Map labels to binary (0/1) for binary classification.
        
        Args:
            labels: List of labels
            positive_class: Class to map to 1 (default: first class)
            
        Returns:
            List[int]: Binary labels
        """
        if not labels:
            return []
        
        unique_labels = sorted(set(str(l) for l in labels if l is not None))
        
        if len(unique_labels) < 2:
            self.logger.warning("Less than 2 classes found, binary mapping may not be meaningful")
        
        positive_class = positive_class or unique_labels[-1]  # Default to last class
        
        binary = [1 if str(l) == positive_class else 0 for l in labels if l is not None]
        
        self.logger.info(f"Mapped labels to binary: {len(binary)} samples")
        return binary
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get label processing statistics."""
        return self._stats.copy()