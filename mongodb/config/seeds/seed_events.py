from datetime import datetime, timedelta
import random
from ..models.event import EventType, Protocol
from ..repositories.event_repository import EventRepository

def generate_event_data():
    """Generate sample event data"""
    
    sources = ["192.168.1.5", "192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9"]
    destinations = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13"]
    protocols = [Protocol.TCP, Protocol.UDP, Protocol.SSH, Protocol.HTTP, Protocol.DNS]
    event_types = [EventType.NETWORK_CONNECTION, EventType.AUTHENTICATION, 
                   EventType.HTTP_REQUEST, EventType.DNS_QUERY]
    source_hostnames = ["PC-01", "PC-02", "PC-03", "WORKSTATION-01", "LAPTOP-01"]
    dest_hostnames = ["Server-01", "Server-02", "DB-01", "APP-01", "FW-01"]
    
    events = []
    base_time = datetime.utcnow() - timedelta(days=1)
    
    for i in range(100):
        timestamp = base_time + timedelta(seconds=random.randint(0, 86400))
        source = random.choice(sources)
        destination = random.choice(destinations)
        protocol = random.choice(protocols)
        event_type = random.choice(event_types)
        
        # Simulate some anomalies
        is_anomaly = random.random() < 0.05  # 5% anomalous
        anomaly_score = random.uniform(0.7, 0.99) if is_anomaly else random.uniform(0, 0.3)
        
        event = {
            "event_id": f"EVT-{i+1:04d}",
            "timestamp": timestamp,
            "source": source,
            "source_port": random.randint(1024, 65535) if source != "192.168.1.5" else 22,
            "destination": destination,
            "destination_port": random.randint(1, 1024),
            "protocol": protocol,
            "event_type": event_type,
            "user": f"user{random.randint(1, 10)}" if random.random() > 0.5 else None,
            "process": f"process{random.randint(1, 5)}" if random.random() > 0.5 else None,
            "command_line": f"/usr/bin/process{random.randint(1, 5)} -c" if random.random() > 0.5 else None,
            "message": f"{event_type.value} from {source} to {destination}",
            "severity": random.choice(["INFO", "WARN", "ERROR"]) if random.random() > 0.7 else None,
            "raw_log": f"RAW: {event_type.value} {source} -> {destination}",
            "normalized_data": {},
            "tags": ["network", "security"] if random.random() > 0.5 else [],
            "is_anomaly": is_anomaly,
            "anomaly_score": anomaly_score,
            "source_hostname": random.choice(source_hostnames),
            "destination_hostname": random.choice(dest_hostnames),
            "bytes_sent": random.randint(64, 65535),
            "bytes_received": random.randint(64, 65535),
            "duration": random.uniform(0.1, 10.0),
            "source_type": "NETWORK"
        }
        events.append(event)
    
    return events

def seed_events():
    """Seed events collection with sample data"""
    
    event_repo = EventRepository()
    
    # Clear existing events
    event_repo.delete_many({})
    
    events = generate_event_data()
    result = event_repo.create_events_bulk(events)
    
    print(f"Seeded {len(events)} events")
    print(f"Anomalous events: {len([e for e in events if e['is_anomaly']])}")
    
    return events

if __name__ == "__main__":
    seed_events()