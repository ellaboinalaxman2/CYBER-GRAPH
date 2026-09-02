"""Script to prepare sample data for Member 3 - AI Engine."""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Error: {e}")
    print("Please install required packages: pip install pandas numpy")
    sys.exit(1)


class SampleDataPreparer:
    """
    Prepares sample data for Member 3.
    """
    
    def __init__(self):
        """Initialize the sample data preparer."""
        # Create directories
        self.data_dir = Path("data")
        self.sample_dir = self.data_dir / "samples"
        self.processed_dir = self.data_dir / "processed"
        self.feature_dir = self.data_dir / "features"
        
        self.sample_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.feature_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = print
        
        # Device names
        self.devices = [
            "PC-01", "PC-02", "PC-03", "PC-04", "PC-05",
            "SERVER-01", "SERVER-02", "SERVER-03",
            "DB-01", "DB-02",
            "FW-01", "FW-02",
            "ROUTER-01", "ROUTER-02",
            "APP-01", "APP-02",
        ]
        
        # Event types
        self.event_types = [
            "LOGIN_SUCCESS", "LOGIN_FAILURE", "LOGIN_LOCKOUT",
            "NETWORK_CONNECTION", "NETWORK_DISCONNECTION",
            "FIREWALL_ALLOW", "FIREWALL_DENY", "FIREWALL_DROP",
            "FILE_ACCESS", "FILE_MODIFIED", "FILE_DELETED",
            "ALERT", "SYSTEM_EVENT",
        ]
        
        # Protocols
        self.protocols = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "SSH", "FTP", "DNS"]
        
        # Actions
        self.actions = ["ALLOW", "DENY", "BLOCK", "DROP", "LOG"]
        
        # Severities
        self.severities = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def prepare_events(self, count: int = 100) -> List[Dict[str, Any]]:
        """Prepare sample events."""
        print(f"Preparing {count} sample events...")
        
        events = []
        for i in range(count):
            source = np.random.choice(self.devices)
            dest = np.random.choice([d for d in self.devices if d != source] or self.devices)
            
            # Generate timestamp (within last 24 hours)
            timestamp = datetime.utcnow() - pd.Timedelta(
                hours=np.random.randint(0, 24),
                minutes=np.random.randint(0, 59),
                seconds=np.random.randint(0, 59),
            )
            
            event = {
                "event_id": f"SAMPLE-{i:08d}",
                "timestamp": timestamp.isoformat() + "Z",
                "event_type": np.random.choice(self.event_types),
                "source_ip": f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
                "destination_ip": f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
                "source_port": np.random.randint(1024, 65535),
                "destination_port": np.random.choice([22, 80, 443, 3306, 3389, 5432]),
                "protocol": np.random.choice(self.protocols),
                "action": np.random.choice(self.actions),
                "severity": np.random.choice(self.severities),
                "user": f"user{np.random.randint(1, 100)}",
                "hostname": source,
                "raw_source": "sample",
                "message": f"Sample event {i}",
                "tags": [np.random.choice(["network", "security", "system", "authentication"])],
            }
            events.append(event)
        
        # Save to file
        output_file = self.sample_dir / "sample_events.json"
        with open(output_file, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        
        print(f"Saved {len(events)} events to {output_file}")
        return events
    
    def prepare_graph(self, nodes: int = 15, edges: int = 25) -> Dict[str, Any]:
        """Prepare sample graph."""
        print(f"Preparing sample graph ({nodes} nodes, {edges} edges)...")
        
        # Generate nodes
        node_list = []
        node_types = ["device", "user", "application", "database", "firewall", "router"]
        
        selected_devices = np.random.choice(self.devices, min(nodes, len(self.devices)), replace=False)
        
        for device in selected_devices:
            node = {
                "node_id": device,
                "node_type": np.random.choice(node_types),
                "hostname": f"{device.lower()}.example.com",
                "ip_address": f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
                "device_type": np.random.choice(["workstation", "server", "firewall", "router", "database"]),
                "os": np.random.choice(["Windows 10", "Windows Server", "Ubuntu 22.04", "CentOS 7", "macOS"]),
                "criticality": np.random.randint(1, 10),
                "department": np.random.choice(["Engineering", "IT", "Finance", "HR", "Security"]),
                "owner": f"Team {np.random.choice(['A', 'B', 'C'])}",
                "tags": [np.random.choice(["production", "development", "testing", "critical"])],
                "properties": {},
            }
            node_list.append(node)
        
        # Generate edges
        edge_list = []
        relationship_types = ["CONNECTS_TO", "ACCESSES", "AUTHENTICATES_TO", "COMMUNICATES_WITH"]
        
        for _ in range(min(edges, len(node_list) * 2)):
            source = np.random.choice(node_list)
            target = np.random.choice([n for n in node_list if n['node_id'] != source['node_id']] or node_list)
            
            edge = {
                "source_id": source['node_id'],
                "target_id": target['node_id'],
                "relationship_type": np.random.choice(relationship_types),
                "properties": {
                    "protocol": np.random.choice(self.protocols),
                    "port": np.random.choice([22, 80, 443, 3306, 3389]),
                    "frequency": np.random.randint(1, 100),
                    "first_seen": (datetime.utcnow() - pd.Timedelta(days=np.random.randint(1, 30))).isoformat() + "Z",
                },
                "weight": np.random.uniform(0.5, 1.0),
            }
            edge_list.append(edge)
        
        graph = {
            "nodes": node_list,
            "edges": edge_list,
            "graph_id": f"SAMPLE-GRAPH-{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "source": "sample_loader",
                "nodes_count": len(node_list),
                "edges_count": len(edge_list),
            },
        }
        
        # Save to file
        output_file = self.sample_dir / "sample_graph.json"
        with open(output_file, 'w') as f:
            json.dump(graph, f, indent=2, default=str)
        
        print(f"Saved graph to {output_file}")
        return graph
    
    def prepare_features(self, count: int = 100) -> Dict[str, Any]:
        """Prepare sample features."""
        print(f"Preparing {count} sample features...")
        
        features = []
        for i in range(count):
            feature = {
                "node_id": f"NODE-{i:04d}",
                "connection_count": np.random.randint(0, 50),
                "failed_login_count": np.random.randint(0, 20),
                "successful_login_count": np.random.randint(0, 10),
                "incoming_connections": np.random.randint(0, 30),
                "outgoing_connections": np.random.randint(0, 30),
                "protocol_diversity": np.random.randint(1, 5),
                "avg_session_duration": np.random.uniform(0, 300),
                "alert_count": np.random.randint(0, 10),
                "criticality": np.random.randint(1, 10),
                "label": np.random.choice([0, 1], p=[0.7, 0.3]),
            }
            features.append(feature)
        
        # Create DataFrame
        df = pd.DataFrame(features)
        
        # Save to CSV
        output_file = self.feature_dir / "sample_features.csv"
        df.to_csv(output_file, index=False)
        
        print(f"Saved {len(features)} features to {output_file}")
        
        return {"features": features, "dataframe": df}
    
    def prepare_complete_dataset(self) -> Dict[str, Any]:
        """Prepare complete sample dataset."""
        print("Preparing complete sample dataset...")
        
        events = self.prepare_events(100)
        graph = self.prepare_graph(15, 25)
        features = self.prepare_features(100)
        
        dataset = {
            "dataset_name": "sample",
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "events": events,
            "graph": graph,
            "features": {
                "data": features["features"],
                "columns": list(features["dataframe"].columns),
            },
            "statistics": {
                "total_events": len(events),
                "total_nodes": len(graph.get("nodes", [])),
                "total_edges": len(graph.get("edges", [])),
                "total_features": len(features["features"]),
            },
        }
        
        # Save combined dataset
        output_file = self.processed_dir / "sample_dataset.json"
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2, default=str)
        
        print(f"Complete dataset saved to {output_file}")
        return dataset


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Prepare sample data for Member 3")
    parser.add_argument(
        "--events",
        type=int,
        default=100,
        help="Number of events to generate"
    )
    parser.add_argument(
        "--nodes",
        type=int,
        default=15,
        help="Number of nodes in graph"
    )
    parser.add_argument(
        "--edges",
        type=int,
        default=25,
        help="Number of edges in graph"
    )
    parser.add_argument(
        "--features",
        type=int,
        default=100,
        help="Number of feature samples"
    )
    parser.add_argument(
        "--complete",
        action="store_true",
        help="Prepare complete dataset"
    )
    
    args = parser.parse_args()
    
    preparer = SampleDataPreparer()
    
    if args.complete:
        dataset = preparer.prepare_complete_dataset()
        print("\n=== Complete Dataset Prepared ===")
        print(f"Events: {dataset['statistics']['total_events']}")
        print(f"Nodes: {dataset['statistics']['total_nodes']}")
        print(f"Edges: {dataset['statistics']['total_edges']}")
        print(f"Features: {dataset['statistics']['total_features']}")
    else:
        events = preparer.prepare_events(args.events)
        graph = preparer.prepare_graph(args.nodes, args.edges)
        features = preparer.prepare_features(args.features)
        
        print("\n=== Sample Data Prepared ===")
        print(f"Events: {len(events)}")
        print(f"Graph: {len(graph.get('nodes', []))} nodes, {len(graph.get('edges', []))} edges")
        print(f"Features: {len(features['features'])}")
    
    print("\nData saved to:")
    print(f"  - Samples: {preparer.sample_dir}")
    print(f"  - Processed: {preparer.processed_dir}")
    print(f"  - Features: {preparer.feature_dir}")
    
    return 0


if __name__ == "__main__":
    main()