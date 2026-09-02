"""Generate sample data for testing."""

import json
import csv
import os
from datetime import datetime, timedelta
import random
import argparse
from pathlib import Path


def generate_json_events(count: int = 100, output_file: str = "data/input/batch/sample_events.json"):
    """Generate sample JSON events."""
    events = []
    
    for i in range(count):
        event = {
            "event_id": f"EVT-{i:08d}",
            "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(0, 1000))).isoformat() + "Z",
            "event_type": random.choice([
                "NETWORK_CONNECTION", "LOGIN_SUCCESS", "LOGIN_FAILURE",
                "FIREWALL_ALLOW", "FIREWALL_DENY", "ALERT"
            ]),
            "source_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "destination_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "source_port": random.randint(1024, 65535),
            "destination_port": random.choice([22, 80, 443, 3389, 3306]),
            "protocol": random.choice(["TCP", "UDP", "ICMP"]),
            "action": random.choice(["ALLOW", "DENY", "BLOCK"]),
            "severity": random.choice(["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]),
        }
        events.append(event)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"Generated {count} JSON events in {output_file}")


def generate_csv_events(count: int = 100, output_file: str = "data/input/batch/sample_events.csv"):
    """Generate sample CSV events."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["event_id", "timestamp", "event_type", "source_ip", "destination_ip", "action"])
        
        for i in range(count):
            writer.writerow([
                f"EVT-{i:08d}",
                (datetime.utcnow() - timedelta(minutes=random.randint(0, 1000))).isoformat() + "Z",
                random.choice(["LOGIN_SUCCESS", "LOGIN_FAILURE", "NETWORK_CONNECTION"]),
                f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                random.choice(["ALLOW", "DENY"]),
            ])
    
    print(f"Generated {count} CSV events in {output_file}")


def generate_syslog_events(count: int = 100, output_file: str = "data/input/batch/sample_logs.log"):
    """Generate sample syslog events."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    hosts = ["server01", "server02", "firewall01", "pc01", "pc02"]
    
    with open(output_file, 'w') as f:
        for i in range(count):
            month = random.choice(months)
            day = random.randint(1, 28)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            host = random.choice(hosts)
            
            log_line = f"{month} {day:02d} {hour:02d}:{minute:02d}:{second:02d} {host} sshd[{random.randint(1000, 9999)}]: "
            
            event_type = random.choice(["success", "failure", "connection"])
            if event_type == "success":
                log_line += f"Accepted password for {random.choice(['root', 'admin', 'user'])} from 192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            elif event_type == "failure":
                log_line += f"Failed password for invalid user {random.choice(['admin', 'root', 'test'])} from 192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            else:
                log_line += f"Connection closed by 192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
            f.write(log_line + "\n")
    
    print(f"Generated {count} syslog events in {output_file}")


def main():
    """Generate all sample data."""
    parser = argparse.ArgumentParser(description="Generate sample data for testing")
    parser.add_argument("--count", type=int, default=100, help="Number of events to generate")
    parser.add_argument("--format", choices=["json", "csv", "syslog", "all"], default="all", help="Format to generate")
    
    args = parser.parse_args()
    
    if args.format in ["json", "all"]:
        generate_json_events(args.count)
    
    if args.format in ["csv", "all"]:
        generate_csv_events(args.count)
    
    if args.format in ["syslog", "all"]:
        generate_syslog_events(args.count)
    
    print("\nSample data generation complete!")


if __name__ == "__main__":
    main()