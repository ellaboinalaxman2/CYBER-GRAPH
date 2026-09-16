from datetime import datetime, timedelta
import random
from ..models.alert import AlertSeverity, AlertStatus
from ..repositories.alert_repository import AlertRepository
from ..repositories.event_repository import EventRepository

def generate_alert_data(events):
    """Generate sample alert data from events"""
    
    alerts = []
    attack_types = ["Lateral Movement", "Data Exfiltration", "Privilege Escalation", 
                   "Malware Activity", "Command and Control", "Port Scanning",
                   "Brute Force Attack", "DDoS Attack", "SQL Injection"]
    mitre_techniques = {
        "Lateral Movement": "T1021",
        "Data Exfiltration": "T1048",
        "Privilege Escalation": "T1068",
        "Malware Activity": "T1204",
        "Command and Control": "T1071",
        "Port Scanning": "T1046",
        "Brute Force Attack": "T1110",
        "DDoS Attack": "T1498",
        "SQL Injection": "T1190"
    }
    
    # Get anomalous events
    anomalous_events = [e for e in events if e['is_anomaly']]
    
    if not anomalous_events:
        print("No anomalous events found, using random events")
        anomalous_events = random.sample(events, min(20, len(events)))
    
    for i, event in enumerate(anomalous_events[:20]):
        attack_type = random.choice(attack_types)
        risk_score = random.randint(50, 98)
        severity = AlertSeverity.CRITICAL if risk_score >= 81 else \
                   AlertSeverity.HIGH if risk_score >= 61 else \
                   AlertSeverity.MEDIUM if risk_score >= 31 else AlertSeverity.LOW
        
        status = random.choice([AlertStatus.OPEN, AlertStatus.UNDER_INVESTIGATION, 
                                AlertStatus.CONFIRMED])
        
        alert = {
            "alert_id": f"ALT-{i+1:04d}",
            "incident_id": f"INC-{i//3 + 1:04d}" if i % 3 == 0 else None,
            "timestamp": event['timestamp'] + timedelta(seconds=random.randint(0, 300)),
            "severity": severity,
            "status": status,
            "risk_score": risk_score,
            "confidence": random.uniform(0.7, 0.99),
            "attack_type": attack_type,
            "attack_technique": attack_type,
            "attack_technique_id": mitre_techniques.get(attack_type, "T0000"),
            "source": event['source'],
            "target": event['destination'],
            "description": f"Potential {attack_type} detected from {event['source']} to {event['destination']}",
            "events": [event['event_id']],
            "affected_nodes": [event['source_hostname'], event['destination_hostname']],
            "attack_path": [event['source_hostname'], event['destination_hostname']],
            "reconstruction_details": {
                "path_sequence": [event['source_hostname'], event['destination_hostname']]
            },
            "mitre_mapping": {
                "technique_id": mitre_techniques.get(attack_type, "T0000"),
                "technique_name": attack_type,
                "tactic": "Lateral Movement" if attack_type == "Lateral Movement" else "Unknown"
            },
            "behavioral_evidence": [f"Suspicious connection from {event['source']}"],
            "recommendations": ["Investigate suspicious connection", "Review access logs"],
            "assigned_to": None,
            "investigation_notes": [],
            "blockchain_hash": None,
            "blockchain_tx_id": None,
            "metadata": {},
            "escalated": random.random() > 0.7
        }
        alerts.append(alert)
    
    return alerts

def seed_alerts():
    """Seed alerts collection with sample data"""
    
    alert_repo = AlertRepository()
    event_repo = EventRepository()
    
    # Get existing events
    events = event_repo.get_events(limit=200)
    
    if not events:
        print("No events found, seeding events first...")
        from .seed_events import seed_events
        events = seed_events()
    
    # Clear existing alerts
    alert_repo.delete_many({})
    
    alerts = generate_alert_data(events)
    for alert in alerts:
        alert_repo.create_alert(alert)
    
    print(f"Seeded {len(alerts)} alerts")
    
    # Print statistics
    stats = alert_repo.get_alert_statistics()
    print(f"Alert statistics: {stats}")
    
    return alerts

if __name__ == "__main__":
    seed_alerts()