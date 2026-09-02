"""Tests for queue system."""

import pytest
import time
import json
import threading

from src.queue import RedisClient, DeadLetterQueue, QueueManager
from src.workers import EventWorker, WorkerPool


class TestRedisClient:
    """Tests for RedisClient."""
    
    def test_singleton(self):
        """Test singleton pattern."""
        client1 = RedisClient()
        client2 = RedisClient()
        assert client1 is client2
    
    def test_ping(self):
        """Test ping."""
        client = RedisClient()
        # Should not raise exception
        client.ping()


class TestDeadLetterQueue:
    """Tests for DeadLetterQueue."""
    
    def test_add_dead_letter(self):
        """Test adding a dead letter."""
        dlq = DeadLetterQueue("test_dlq")
        result = dlq.add(
            message={"test": "value"},
            error="Test error",
            retry_count=1,
            source_queue="test_queue",
        )
        assert result is True
    
    def test_get_count(self):
        """Test getting dead letter count."""
        dlq = DeadLetterQueue("test_dlq")
        count = dlq.get_count()
        assert count >= 0


class TestQueueManager:
    """Tests for QueueManager."""
    
    def test_create_queue(self):
        """Test creating a queue."""
        manager = QueueManager()
        manager.create_queue("test_queue")
        stats = manager.get_queue_stats("test_queue")
        assert stats["name"] == "test_queue"
    
    def test_produce_consume(self):
        """Test producing and consuming messages."""
        manager = QueueManager()
        manager.create_queue("test_queue")
        
        # Create a flag to track consumption
        consumed = threading.Event()
        consumed_message = None
        
        def callback(message):
            nonlocal consumed_message
            consumed_message = message
            consumed.set()
        
        # Start consumer
        manager.start()
        manager.consume("test_queue", callback)
        
        # Produce message
        manager.produce("test_queue", {"test": "value"})
        
        # Wait for consumption
        consumed.wait(timeout=2.0)
        
        assert consumed.is_set()
        assert consumed_message is not None
        assert consumed_message.get("test") == "value"
        
        manager.stop()


class TestEventWorker:
    """Tests for EventWorker."""
    
    def test_worker_creation(self):
        """Test worker creation."""
        worker = EventWorker("test_worker")
        assert worker.name == "test_worker"
    
    def test_process_message(self):
        """Test processing a message."""
        worker = EventWorker("test_worker")
        
        message = {
            "event_id": "EVT-001",
            "event": {
                "source_ip": "192.168.1.10",
                "destination_ip": "192.168.1.20",
                "event_type": "NETWORK_CONNECTION",
            }
        }
        
        result = worker.process(message)
        assert result["status"] == "success"
        assert result["event_id"] == "EVT-001"


class TestWorkerPool:
    """Tests for WorkerPool."""
    
    def test_add_worker(self):
        """Test adding a worker."""
        pool = WorkerPool(max_workers=2)
        worker = EventWorker("test_worker")
        pool.add_worker(worker)
        assert len(pool.workers) == 1
    
    def test_start_stop(self):
        """Test starting and stopping the pool."""
        pool = WorkerPool(max_workers=1)
        worker = EventWorker("test_worker")
        pool.add_worker(worker)
        
        pool.start()
        assert pool._is_running is True
        
        pool.stop()
        assert pool._is_running is False