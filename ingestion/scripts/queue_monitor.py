"""Queue monitoring script."""

import time
import json
from datetime import datetime

from src.queue import QueueManager
from src.core.logging import setup_logging


def monitor_queue(queue_name: str = "events", interval: int = 5):
    """
    Monitor a queue.
    
    Args:
        queue_name: Name of the queue to monitor
        interval: Monitoring interval in seconds
    """
    setup_logging()
    manager = QueueManager()
    manager.create_queue(queue_name)
    
    print(f"Monitoring queue: {queue_name}")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        while True:
            stats = manager.get_queue_stats(queue_name)
            overall_stats = manager.get_stats()
            
            print(f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"Queue Size: {stats.get('size', 0)}")
            print(f"Delayed Messages: {stats.get('delayed', 0)}")
            print(f"Dead Letter Count: {overall_stats.get('dead_letter_count', 0)}")
            print(f"Messages Produced: {overall_stats.get('messages_produced', 0)}")
            print(f"Messages Consumed: {overall_stats.get('messages_consumed', 0)}")
            print(f"Messages Failed: {overall_stats.get('messages_failed', 0)}")
            print("-" * 60)
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Monitor a queue")
    parser.add_argument("--queue", default="events", help="Queue name")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval (seconds)")
    args = parser.parse_args()
    
    monitor_queue(args.queue, args.interval)