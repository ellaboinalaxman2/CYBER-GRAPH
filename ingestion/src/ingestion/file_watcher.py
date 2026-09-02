"""File watcher for monitoring directories."""

import os
import time
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from datetime import datetime
import threading

from src.core.logging import get_logger


class FileWatcher:
    """
    Watches directories for new files.
    
    Supports:
    - Directory monitoring
    - File pattern matching
    - Callback on new files
    - Polling-based detection
    """
    
    def __init__(self, poll_interval: int = 5):
        """
        Initialize the file watcher.
        
        Args:
            poll_interval: Polling interval in seconds
        """
        self.logger = get_logger("ingestion.watcher")
        self.poll_interval = poll_interval
        self.watches: Dict[str, Dict[str, Any]] = {}
        self._is_running = False
        self._thread = None
        self._callbacks: List[Callable] = []
    
    def add_watch(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = False,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        Add a directory to watch.
        
        Args:
            directory: Directory to watch
            pattern: File pattern to match
            recursive: Whether to watch subdirectories
            callback: Callback when new file is found
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        self.watches[str(directory)] = {
            "directory": str(directory),
            "pattern": pattern,
            "recursive": recursive,
            "callback": callback,
            "files_seen": self._get_files(str(directory), pattern, recursive),
        }
        
        self.logger.info(f"Added watch: {directory} ({pattern})")
    
    def remove_watch(self, directory: str) -> None:
        """Remove a directory watch."""
        if directory in self.watches:
            del self.watches[directory]
            self.logger.info(f"Removed watch: {directory}")
    
    def register_callback(self, callback: Callable) -> None:
        """
        Register a callback for all new files.
        
        Args:
            callback: Callback function
        """
        self._callbacks.append(callback)
    
    def start(self) -> None:
        """Start the file watcher."""
        if self._is_running:
            self.logger.warning("File watcher is already running")
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        self.logger.info("File watcher started")
    
    def stop(self) -> None:
        """Stop the file watcher."""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self.logger.info("File watcher stopped")
    
    def _watch_loop(self) -> None:
        """Main watch loop."""
        self.logger.info("Watch loop started")
        
        while self._is_running:
            try:
                self._check_watches()
            except Exception as e:
                self.logger.error(f"Watch loop error: {e}")
            
            time.sleep(self.poll_interval)
    
    def _check_watches(self) -> None:
        """Check all watches for new files."""
        for watch_id, watch in self.watches.items():
            current_files = self._get_files(
                watch["directory"],
                watch["pattern"],
                watch["recursive"],
            )
            
            # Find new files
            new_files = set(current_files) - set(watch["files_seen"])
            
            if new_files:
                self.logger.info(f"Found {len(new_files)} new files in {watch['directory']}")
                
                for file_path in new_files:
                    # Trigger callbacks
                    self._trigger_callbacks(file_path, watch)
                
                # Update seen files
                watch["files_seen"] = current_files
    
    def _get_files(self, directory: str, pattern: str, recursive: bool) -> List[str]:
        """Get list of files in directory matching pattern."""
        directory = Path(directory)
        
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        # Exclude directories
        return [str(f) for f in files if f.is_file()]
    
    def _trigger_callbacks(self, file_path: str, watch: Dict[str, Any]) -> None:
        """Trigger callbacks for a new file."""
        # Watch-specific callback
        if watch.get("callback"):
            try:
                watch["callback"](file_path)
            except Exception as e:
                self.logger.error(f"Watch callback error: {e}")
        
        # Global callbacks
        for callback in self._callbacks:
            try:
                callback(file_path)
            except Exception as e:
                self.logger.error(f"Global callback error: {e}")
    
    @property
    def is_running(self) -> bool:
        """Check if the watcher is running."""
        return self._is_running