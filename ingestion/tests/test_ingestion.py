"""Tests for ingestion."""

import pytest
import json
import os
import tempfile
from pathlib import Path

from src.ingestion import (
    BatchIngester,
    StreamIngester,
    FileWatcher,
    DataSource,
    DataSourceType,
    DataFormat,
    DataSourceManager,
)


class TestBatchIngester:
    """Tests for BatchIngester."""
    
    def test_ingest_json_file(self):
        """Test ingesting a JSON file."""
        ingester = BatchIngester()
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"id": 1, "event": "test1"},
                {"id": 2, "event": "test2"},
            ], f)
            temp_file = f.name
        
        try:
            result = ingester.ingest_file(temp_file, "test_source")
            assert result["status"] == "completed"
            assert result["events_total"] == 2
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_ingest_csv_file(self):
        """Test ingesting a CSV file."""
        ingester = BatchIngester()
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,event\n1,test1\n2,test2\n")
            temp_file = f.name
        
        try:
            result = ingester.ingest_file(temp_file, "test_source")
            assert result["status"] == "completed"
            assert result["events_total"] == 2
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_get_stats(self):
        """Test getting ingestion statistics."""
        ingester = BatchIngester()
        stats = ingester.get_stats()
        
        assert "files_processed" in stats
        assert "events_processed" in stats
        assert "events_failed" in stats


class TestFileWatcher:
    """Tests for FileWatcher."""
    
    def test_add_watch(self):
        """Test adding a watch."""
        watcher = FileWatcher()
        with tempfile.TemporaryDirectory() as temp_dir:
            watcher.add_watch(temp_dir, pattern="*.txt")
            assert len(watcher.watches) == 1
    
    def test_start_stop(self):
        """Test starting and stopping the watcher."""
        watcher = FileWatcher()
        watcher.start()
        assert watcher.is_running is True
        watcher.stop()
        assert watcher.is_running is False


class TestDataSourceManager:
    """Tests for DataSourceManager."""
    
    def test_get_sources(self):
        """Test getting data sources."""
        manager = DataSourceManager()
        sources = manager.get_enabled_sources()
        assert len(sources) > 0
    
    def test_add_source(self):
        """Test adding a source."""
        manager = DataSourceManager()
        source = DataSource(
            name="test_source",
            type=DataSourceType.FILE,
            format=DataFormat.JSON,
            file_path="test.json",
        )
        manager.add_source(source)
        assert manager.get_source("test_source") is not None
    
    def test_disable_source(self):
        """Test disabling a source."""
        manager = DataSourceManager()
        manager.disable_source("firewall_logs")
        source = manager.get_source("firewall_logs")
        assert source.enabled is False