"""Base worker for processing queue messages."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.logging import get_logger


class BaseWorker(ABC):
    """
    Abstract base class for workers.
    
    Workers process messages from queues.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize the worker.
        
        Args:
            name: Worker name
        """
        self.name = name or self.__class__.__name__
        self.logger = get_logger(f"worker.{self.name}")
        self._stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "last_processed": None,
        }
    
    @abstractmethod
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message.
        
        Args:
            message: Message to process
            
        Returns:
            Dict[str, Any]: Processing result
            
        Raises:
            Exception: If processing fails
        """
        pass
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a message with statistics tracking.
        
        Args:
            message: Message to process
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            result = self.process(message)
            self._stats["successful"] += 1
            self._stats["last_processed"] = datetime.utcnow()
            return result
            
        except Exception as e:
            self._stats["failed"] += 1
            self.logger.error(f"Worker {self.name} failed: {e}")
            raise
        
        finally:
            self._stats["processed"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get worker statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        return {
            **self._stats,
            "name": self.name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }