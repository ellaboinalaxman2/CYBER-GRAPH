"""Dead letter queue handling."""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from src.queue.redis_client import RedisClient
from src.core.logging import get_logger
from src.core.config import settings


class DeadLetterQueue:
    """
    Dead letter queue for failed messages.
    
    Handles:
    - Failed message storage
    - Message retry
    - Message inspection
    - Cleanup
    """
    
    def __init__(self, queue_name: str = "dead_letter"):
        """
        Initialize the dead letter queue.
        
        Args:
            queue_name: Name of the dead letter queue
        """
        self.logger = get_logger("queue.dead_letter")
        self.queue_name = queue_name
        self.redis = RedisClient()
        self._local_storage_dir = Path("data/queue/dead_letter")
        self._local_storage_dir.mkdir(parents=True, exist_ok=True)
    
    def add(
        self,
        message: Dict[str, Any],
        error: str,
        retry_count: int = 0,
        source_queue: Optional[str] = None,
    ) -> bool:
        """
        Add a message to the dead letter queue.
        
        Args:
            message: The failed message
            error: Error description
            retry_count: Number of retry attempts
            source_queue: Original queue name
            
        Returns:
            bool: True if added successfully
        """
        dead_letter = {
            "message": message,
            "error": error,
            "retry_count": retry_count,
            "source_queue": source_queue or "unknown",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "id": f"DL-{datetime.utcnow().timestamp()}-{hash(str(message))}",
        }
        
        try:
            # Try Redis first
            data = json.dumps(dead_letter, default=str)
            result = self.redis.execute('rpush', self.queue_name, data)
            
            if result:
                self.logger.info(f"Added message to dead letter queue: {dead_letter['id']}")
                return True
            else:
                raise Exception("Redis push failed")
                
        except Exception as e:
            self.logger.warning(f"Redis dead letter failed, using local storage: {e}")
            # Fallback to local storage
            return self._store_local(dead_letter)
    
    def _store_local(self, dead_letter: Dict[str, Any]) -> bool:
        """Store dead letter locally."""
        try:
            filename = f"{dead_letter['id']}.json"
            filepath = self._local_storage_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(dead_letter, f, indent=2)
            
            self.logger.info(f"Stored dead letter locally: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store dead letter locally: {e}")
            return False
    
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all dead letters.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List[Dict[str, Any]]: Dead letters
        """
        dead_letters = []
        
        # Try Redis first
        try:
            items = self.redis.execute('lrange', self.queue_name, 0, limit - 1)
            for item in items:
                try:
                    dead_letters.append(json.loads(item))
                except:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"Redis dead letter retrieval failed: {e}")
        
        # If Redis failed or empty, try local storage
        if not dead_letters:
            local_files = list(self._local_storage_dir.glob("*.json"))
            for filepath in local_files[:limit]:
                try:
                    with open(filepath, 'r') as f:
                        dead_letters.append(json.load(f))
                except Exception as e:
                    self.logger.error(f"Failed to read local dead letter {filepath}: {e}")
        
        return dead_letters
    
    def get_count(self) -> int:
        """
        Get the number of dead letters.
        
        Returns:
            int: Number of dead letters
        """
        try:
            return self.redis.execute('llen', self.queue_name)
        except Exception:
            return len(list(self._local_storage_dir.glob("*.json")))
    
    def retry(self, dead_letter_id: str, target_queue: str) -> bool:
        """
        Retry a dead letter by moving it to a queue.
        
        Args:
            dead_letter_id: ID of the dead letter
            target_queue: Queue to move the message to
            
        Returns:
            bool: True if retry was successful
        """
        # Find and remove the dead letter
        dead_letter = None
        
        # Try Redis
        try:
            items = self.redis.execute('lrange', self.queue_name, 0, -1)
            for i, item in enumerate(items):
                try:
                    data = json.loads(item)
                    if data.get('id') == dead_letter_id:
                        dead_letter = data
                        self.redis.execute('lrem', self.queue_name, 1, item)
                        break
                except:
                    pass
        except Exception as e:
            self.logger.warning(f"Redis dead letter retry failed: {e}")
        
        # Try local storage
        if not dead_letter:
            local_files = list(self._local_storage_dir.glob("*.json"))
            for filepath in local_files:
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data.get('id') == dead_letter_id:
                            dead_letter = data
                            filepath.unlink()
                            break
                except Exception as e:
                    self.logger.error(f"Failed to read local dead letter {filepath}: {e}")
        
        if dead_letter:
            # Remove the message from the dead letter
            message = dead_letter.get('message', {})
            
            # Add to target queue
            try:
                self.redis.execute('rpush', target_queue, json.dumps(message, default=str))
                self.logger.info(f"Retried dead letter {dead_letter_id} to {target_queue}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to retry dead letter {dead_letter_id}: {e}")
                return False
        
        self.logger.warning(f"Dead letter not found: {dead_letter_id}")
        return False
    
    def clear(self) -> int:
        """
        Clear all dead letters.
        
        Returns:
            int: Number of dead letters cleared
        """
        count = 0
        
        # Clear Redis
        try:
            count += self.redis.execute('llen', self.queue_name)
            self.redis.execute('del', self.queue_name)
        except Exception as e:
            self.logger.warning(f"Redis dead letter clear failed: {e}")
        
        # Clear local storage
        local_files = list(self._local_storage_dir.glob("*.json"))
        for filepath in local_files:
            try:
                filepath.unlink()
                count += 1
            except Exception as e:
                self.logger.error(f"Failed to delete local dead letter {filepath}: {e}")
        
        return count