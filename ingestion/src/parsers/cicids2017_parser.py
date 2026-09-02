"""CICIDS2017 parser."""

from typing import Optional, Dict, Any
from src.parsers.base import BaseParser
from src.models.raw_event import RawEvent
import csv
import io

class CICIDS2017Parser(BaseParser):
    """
    Parser for CICIDS2017 dataset format (CSV).
    Maps columns to normalized event structure.
    """
    
    def __init__(self):
        super().__init__(parser_name="CICIDS2017Parser")
        
    def parse(self, raw_event: RawEvent) -> Optional[Dict[str, Any]]:
        try:
            # Assuming raw_event.raw_content is a single CSV row string
            f = io.StringIO(raw_event.raw_content)
            reader = csv.reader(f)
            row = next(reader)
            
            # This is a simplified mapping for demonstration
            # CICIDS2017 has ~85 columns.
            # Example columns we care about:
            # Source IP, Source Port, Destination IP, Destination Port, Protocol, Timestamp, Label
            # In standard CICIDS:
            # Flow ID (0), Source IP (1), Source Port (2), Destination IP (3), Destination Port (4),
            # Protocol (5), Timestamp (6), ... Label (last column)
            
            if len(row) < 10:
                return None
                
            src_ip = row[1].strip()
            src_port = row[2].strip()
            dst_ip = row[3].strip()
            dst_port = row[4].strip()
            protocol = row[5].strip()
            timestamp = row[6].strip()
            label = row[-1].strip()
            
            parsed = {
                "timestamp": timestamp,
                "source_ip": src_ip,
                "source_port": int(src_port) if src_port.isdigit() else 0,
                "destination_ip": dst_ip,
                "destination_port": int(dst_port) if dst_port.isdigit() else 0,
                "protocol": protocol,
                "action": "allow", # default
                "severity": 1 if label == "BENIGN" else 8,
                "labels": [label] if label != "BENIGN" else [],
                "event_type": "network_flow",
                "raw_event_id": raw_event.id
            }
            
            self._update_stats(True)
            return parsed
        except Exception as e:
            self.logger.error(f"Failed to parse CICIDS row: {e}")
            self._update_stats(False)
            return None

    @staticmethod
    def supports(source_type: str) -> bool:
        return source_type.lower() == "cicids2017"
