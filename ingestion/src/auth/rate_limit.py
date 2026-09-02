"""Rate limiting implementation."""

import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import threading

from src.core.logging import get_logger


class RateLimiter:
    """
    Rate limiter for API endpoints.
    
    Features:
    - Per-user rate limiting
    - Per-IP rate limiting
    - Sliding window
    - Configurable limits
    """
    
    def __init__(self):
        """Initialize the rate limiter."""
        self.logger = get_logger("auth.rate_limit")
        self.limits: Dict[str, Dict[str, Any]] = {}
        self.requests: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
    
    def add_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60,
        user_type: str = "ip",
    ) -> None:
        """
        Add a rate limit.
        
        Args:
            key: Key identifier (IP, username, etc.)
            max_requests: Maximum requests in the window
            window_seconds: Time window in seconds
            user_type: Type of user (ip, user, etc.)
        """
        self.limits[key] = {
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "user_type": user_type,
        }
        self.logger.info(f"Added rate limit for {key}: {max_requests}/{window_seconds}s")
    
    def check_limit(self, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed.
        
        Args:
            key: Key to check
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (allowed, info)
        """
        if key not in self.limits:
            # No limit configured, allow
            return True, {"allowed": True}
        
        limit = self.limits[key]
        max_requests = limit["max_requests"]
        window_seconds = limit["window_seconds"]
        
        with self._lock:
            now = time.time()
            cutoff = now - window_seconds
            
            # Clean old requests
            self.requests[key] = [ts for ts in self.requests[key] if ts > cutoff]
            
            # Check limit
            if len(self.requests[key]) >= max_requests:
                # Rate limited
                reset_time = self.requests[key][0] + window_seconds if self.requests[key] else now + window_seconds
                return False, {
                    "allowed": False,
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": reset_time,
                    "window_seconds": window_seconds,
                }
            
            # Add request
            self.requests[key].append(now)
            
            return True, {
                "allowed": True,
                "limit": max_requests,
                "remaining": max_requests - len(self.requests[key]),
                "reset": now + window_seconds,
                "window_seconds": window_seconds,
            }
    
    def get_stats(self, key: str) -> Dict[str, Any]:
        """
        Get rate limit statistics for a key.
        
        Args:
            key: Key to get stats for
            
        Returns:
            Dict[str, Any]: Statistics
        """
        if key not in self.limits:
            return {"exists": False}
        
        limit = self.limits[key]
        max_requests = limit["max_requests"]
        window_seconds = limit["window_seconds"]
        
        with self._lock:
            now = time.time()
            cutoff = now - window_seconds
            active_requests = [ts for ts in self.requests[key] if ts > cutoff]
            
            return {
                "exists": True,
                "max_requests": max_requests,
                "window_seconds": window_seconds,
                "current_requests": len(active_requests),
                "remaining": max_requests - len(active_requests),
            }


# Global rate limiter instance
_rate_limiter = RateLimiter()

# Default limits
_rate_limiter.add_limit("default_ip", max_requests=100, window_seconds=60, user_type="ip")
_rate_limiter.add_limit("default_user", max_requests=200, window_seconds=60, user_type="user")