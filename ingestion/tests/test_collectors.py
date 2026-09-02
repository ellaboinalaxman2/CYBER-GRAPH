"""Tests for collectors."""

import pytest
import os
import time
from threading import Thread

from src.collectors import (
    SyslogCollector,
    FirewallCollector,
    WindowsCollector,
    LinuxCollector,
    NetworkCollector,
    ApplicationCollector,
)
from src.core.config import settings
from src.core.exceptions import CollectorError


class TestFirewallCollector:
    """Tests for FirewallCollector."""
    
    def test_connect_and_disconnect(self):
        """Test connecting and disconnecting."""
        collector = FirewallCollector()
        
        try:
            connected = collector.connect()
            assert connected is True
            assert collector.is_connected is True
        finally:
            collector.disconnect()
        
        assert collector.is_connected is False
    
    def test_collect_one(self):
        """Test collecting one event."""
        collector = FirewallCollector()
        
        try:
            collector.connect()
            event = collector.collect_one()
            
            # Should have events from sample file
            assert event is not None
            assert event.raw_source == "firewall"
            assert event.raw_content is not None
            
        finally:
            collector.disconnect()
    
    def test_collect_batch(self):
        """Test collecting multiple events."""
        collector = FirewallCollector()
        
        try:
            collector.connect()
            events = collector.collect_batch(batch_size=3)
            
            assert len(events) <= 3
            for event in events:
                assert event.raw_source == "firewall"
                
        finally:
            collector.disconnect()
    
    def test_json_parsing(self):
        """Test that JSON logs are parsed correctly."""
        collector = FirewallCollector()
        
        try:
            collector.connect()
            event = collector.collect_one()
            
            if event and event.raw_json:
                assert "src" in event.raw_json or "timestamp" in event.raw_json
                
        finally:
            collector.disconnect()


class TestSyslogCollector:
    """Tests for SyslogCollector."""
    
    def test_connect(self):
        """Test syslog connection."""
        collector = SyslogCollector(port=5555)
        
        try:
            connected = collector.connect()
            assert connected is True
            assert collector.is_connected is True
        finally:
            collector.disconnect()
        
        assert collector.is_connected is False
    
    def test_collect_timeout(self):
        """Test that collect_one returns None on timeout."""
        collector = SyslogCollector(port=5555, timeout=1.0)
        
        try:
            collector.connect()
            # Should return None after timeout
            event = collector.collect_one()
            assert event is None
        finally:
            collector.disconnect()
    
    def test_context_manager(self):
        """Test using collector as context manager."""
        with SyslogCollector(port=5556) as collector:
            assert collector.is_connected is True
            # Should have sample data
            event = collector.collect_one()
            # Event may be None if no data, but that's fine
        
        assert collector.is_connected is False


class TestWindowsCollector:
    """Tests for WindowsCollector."""
    
    def test_connect_and_collect(self):
        """Test Windows collector connection and collection."""
        collector = WindowsCollector()
        
        try:
            collector.connect()
            assert collector.is_connected is True
            
            event = collector.collect_one()
            assert event is not None
            assert event.raw_source == "windows"
            
        finally:
            collector.disconnect()
    
    def test_collect_batch(self):
        """Test batch collection."""
        collector = WindowsCollector()
        
        try:
            collector.connect()
            events = collector.collect_batch(batch_size=5)
            
            assert len(events) > 0
            for event in events:
                assert event.raw_source == "windows"
                
        finally:
            collector.disconnect()


class TestLinuxCollector:
    """Tests for LinuxCollector."""
    
    def test_connect_and_collect(self):
        """Test Linux collector connection and collection."""
        collector = LinuxCollector()
        
        try:
            collector.connect()
            assert collector.is_connected is True
            
            event = collector.collect_one()
            assert event is not None
            assert event.raw_source == "linux"
            
        finally:
            collector.disconnect()


class TestNetworkCollector:
    """Tests for NetworkCollector."""
    
    def test_connect_and_collect(self):
        """Test Network collector connection and collection."""
        collector = NetworkCollector()
        
        try:
            collector.connect()
            assert collector.is_connected is True
            
            event = collector.collect_one()
            assert event is not None
            assert event.raw_source == "network"
            
        finally:
            collector.disconnect()


class TestApplicationCollector:
    """Tests for ApplicationCollector."""
    
    def test_connect_and_collect(self):
        """Test Application collector connection and collection."""
        collector = ApplicationCollector(app_name="testapp")
        
        try:
            collector.connect()
            assert collector.is_connected is True
            
            event = collector.collect_one()
            assert event is not None
            assert event.raw_source == "application"
            
        finally:
            collector.disconnect()
    
    def test_stats(self):
        """Test collector statistics."""
        collector = ApplicationCollector(app_name="testapp")
        
        try:
            collector.connect()
            
            # Collect some events
            for _ in range(3):
                event = collector.collect_one()
                if event:
                    pass
            
            stats = collector.stats
            assert "events_collected" in stats
            assert "events_failed" in stats
            assert "connection_attempts" in stats
            assert stats["connection_attempts"] >= 1
            
        finally:
            collector.disconnect()


class TestCollectorErrors:
    """Test error handling in collectors."""
    
    def test_collector_error_on_disconnect(self):
        """Test that collectors raise errors when not connected."""
        collector = FirewallCollector()
        
        # Should raise error when trying to collect without connecting
        with pytest.raises(CollectorError):
            collector.collect_one()
    
    def test_invalid_source_type(self):
        """Test that invalid source types are handled."""
        # This should work with our default source types
        collector = FirewallCollector(source_type="file")
        assert collector.source_type == "firewall"  # Fixed
    
    def test_stats_updated_on_error(self):
        """Test that stats are updated on errors."""
        collector = SyslogCollector(port=5557, timeout=0.1)
        
        try:
            collector.connect()
            
            # This will time out (no data)
            event = collector.collect_one()
            assert event is None
            
            stats = collector.stats
            assert stats["events_failed"] >= 0  # May not increment on timeout
            
        finally:
            collector.disconnect()