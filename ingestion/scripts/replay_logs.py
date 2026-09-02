"""Replay logs for testing."""

import time
import json
from typing import Dict, Any, Optional
import argparse
from pathlib import Path

from src.ingestion.batch_ingester import BatchIngester
from src.ingestion.stream_ingester import StreamIngester
from src.core.logging import setup_logging
from src.core.config import settings


class LogReplayer:
    """
    Replays logs for testing.
    
    Supports:
    - Batch replay
    - Streaming replay with delays
    - Custom speed control
    """
    
    def __init__(self):
        """Initialize the log replayer."""
        self.batch_ingester = BatchIngester()
        self.stream_ingester = StreamIngester()
        
    def replay_batch(self, file_path: str) -> None:
        """
        Replay a log file as a batch.
        
        Args:
            file_path: Path to the log file
        """
        print(f"Replaying batch: {file_path}")
        result = self.batch_ingester.ingest_file(file_path, "replay")
        print(f"Result: {json.dumps(result, indent=2)}")
    
    def replay_stream(
        self,
        file_path: str,
        delay: float = 1.0,
        speed: float = 1.0,
    ) -> None:
        """
        Replay a log file as a stream.
        
        Args:
            file_path: Path to the log file
            delay: Delay between events (seconds)
            speed: Speed multiplier
        """
        print(f"Replaying stream: {file_path} (delay: {delay}s, speed: {speed}x)")
        
        # Read file
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Process each line with delay
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Create event
            event = {
                "raw_content": line,
                "line_number": i + 1,
                "source": "replay",
                "collected_at": time.time(),
            }
            
            # Process through pipeline
            from src.pipeline import Pipeline
            pipeline = Pipeline()
            context = pipeline.process_event(event)
            
            if context.is_successful:
                print(f"Processed event {i+1}/{len(lines)}")
            else:
                print(f"Failed to process event {i+1}: {context.errors}")
            
            # Wait
            time.sleep(delay / speed)
        
        print("Stream replay complete")


def main():
    """Replay logs."""
    parser = argparse.ArgumentParser(description="Replay logs for testing")
    parser.add_argument("file", help="Log file to replay")
    parser.add_argument("--mode", choices=["batch", "stream"], default="batch", help="Replay mode")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between events (seconds)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speed multiplier")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    replayer = LogReplayer()
    
    if args.mode == "batch":
        replayer.replay_batch(args.file)
    else:
        replayer.replay_stream(args.file, args.delay, args.speed)


if __name__ == "__main__":
    main()