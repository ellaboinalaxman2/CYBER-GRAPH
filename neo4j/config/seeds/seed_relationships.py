from typing import List, Dict, Any
from ..models.relationship_types import RelationshipType
from ..repositories.relationship_repository import RelationshipRepository
from ..repositories.node_repository import NodeRepository

def generate_relationships() -> List[Dict[str, Any]]:
    """Generate sample relationships for testing"""
    
    relationships = [
        # Workstation to Server connections
        {
            "source_id": "WS-001",
            "target_id": "SRV-001",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "HTTP",
            "port": 443,
            "confidence": 0.95,
            "description": "Workstation accessing web app",
            "frequency": 100,
            "duration": 3600
        },
        {
            "source_id": "WS-002",
            "target_id": "SRV-001",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "HTTP",
            "port": 443,
            "confidence": 0.90,
            "description": "Workstation accessing web app",
            "frequency": 80,
            "duration": 1800
        },
        {
            "source_id": "WS-003",
            "target_id": "SRV-001",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "SSH",
            "port": 22,
            "confidence": 0.85,
            "description": "Developer SSH to app server",
            "frequency": 20,
            "duration": 7200
        },
        {
            "source_id": "WS-003",
            "target_id": "SRV-003",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "SMB",
            "port": 445,
            "confidence": 0.90,
            "description": "Developer accessing file server",
            "frequency": 50,
            "duration": 300
        },
        
        # Server to Database connections
        {
            "source_id": "SRV-001",
            "target_id": "DB-001",
            "type": RelationshipType.ACCESSES,
            "protocol": "PostgreSQL",
            "port": 5432,
            "confidence": 0.95,
            "description": "App server accessing primary database",
            "frequency": 500,
            "duration": 86400
        },
        {
            "source_id": "SRV-001",
            "target_id": "DB-002",
            "type": RelationshipType.ACCESSES,
            "protocol": "MySQL",
            "port": 3306,
            "confidence": 0.85,
            "description": "App server accessing analytics database",
            "frequency": 50,
            "duration": 3600
        },
        {
            "source_id": "SRV-002",
            "target_id": "DB-001",
            "type": RelationshipType.READS_FROM,
            "protocol": "PostgreSQL",
            "port": 5432,
            "confidence": 0.80,
            "description": "Web server reading from database",
            "frequency": 30,
            "duration": 600
        },
        
        # Server to Server connections
        {
            "source_id": "SRV-001",
            "target_id": "SRV-002",
            "type": RelationshipType.COMMUNICATES_WITH,
            "protocol": "HTTP",
            "port": 80,
            "confidence": 0.85,
            "description": "App server to web server API calls",
            "frequency": 200,
            "duration": 1800
        },
        {
            "source_id": "SRV-003",
            "target_id": "SRV-001",
            "type": RelationshipType.DEPENDS_ON,
            "protocol": "HTTP",
            "port": 443,
            "confidence": 0.90,
            "description": "File server depends on app server for auth",
            "frequency": 10,
            "duration": 86400
        },
        {
            "source_id": "SRV-004",
            "target_id": "DB-001",
            "type": RelationshipType.ACCESSES,
            "protocol": "PostgreSQL",
            "port": 5432,
            "confidence": 0.90,
            "description": "Email server accessing database",
            "frequency": 100,
            "duration": 3600
        },
        
        # Network device connections
        {
            "source_id": "FW-001",
            "target_id": "RT-001",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "BGP",
            "port": 179,
            "confidence": 1.0,
            "description": "Firewall to router connection"
        },
        {
            "source_id": "RT-001",
            "target_id": "SW-001",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "LACP",
            "port": 0,
            "confidence": 1.0,
            "description": "Router to switch connection"
        },
        {
            "source_id": "SW-001",
            "target_id": "WS-001",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "Ethernet",
            "port": 1,
            "confidence": 1.0,
            "description": "Switch to workstation connection"
        },
        {
            "source_id": "SW-001",
            "target_id": "SRV-001",
            "type": RelationshipType.CONNECTS_TO,
            "protocol": "Ethernet",
            "port": 2,
            "confidence": 1.0,
            "description": "Switch to server connection"
        },
        
        # Attack path relationships (simulated)
        {
            "source_id": "WS-001",
            "target_id": "IP-MALICIOUS",
            "type": RelationshipType.COMMUNICATES_WITH,
            "protocol": "HTTPS",
            "port": 443,
            "confidence": 0.60,
            "description": "Suspicious C2 communication",
            "risk_score": 85,
            "severity": "HIGH",
            "detection_method": "Network Traffic Analysis",
            "confidence_score": 0.75,
            "evidence": ["Suspicious domain lookup", "Unusual outbound traffic"]
        },
        {
            "source_id": "SRV-001",
            "target_id": "WS-001",
            "type": RelationshipType.LATERAL_MOVEMENT,
            "protocol": "RDP",
            "port": 3389,
            "confidence": 0.55,
            "description": "Potential lateral movement attempt",
            "risk_score": 90,
            "severity": "CRITICAL",
            "detection_method": "Behavioral Analysis",
            "confidence_score": 0.80,
            "evidence": ["Unusual RDP connection", "Out-of-hours access"]
        },
        {
            "source_id": "SRV-001",
            "target_id": "DB-001",
            "type": RelationshipType.LATERAL_MOVEMENT,
            "protocol": "PostgreSQL",
            "port": 5432,
            "confidence": 0.50,
            "description": "Suspicious database access from app server",
            "risk_score": 95,
            "severity": "CRITICAL",
            "detection_method": "Database Activity Monitoring",
            "confidence_score": 0.85,
            "evidence": ["High volume data access", "Sensitive table access"]
        },
        {
            "source_id": "SRV-001",
            "target_id": "IP-MALICIOUS",
            "type": RelationshipType.COMMUNICATES_WITH,
            "protocol": "HTTPS",
            "port": 443,
            "confidence": 0.45,
            "description": "Suspicious data exfiltration attempt",
            "risk_score": 92,
            "severity": "CRITICAL",
            "detection_method": "Data Exfiltration Detection",
            "confidence_score": 0.70,
            "evidence": ["Large data transfer", "Suspicious destination IP"]
        },
        
        # MITRE technique mappings
        {
            "source_id": "MITRE-T1021",
            "target_id": "SRV-001",
            "type": RelationshipType.MITRE_TECHNIQUE,
            "description": "Lateral Movement via Remote Services"
        },
        {
            "source_id": "MITRE-T1048",
            "target_id": "SRV-001",
            "type": RelationshipType.MITRE_TECHNIQUE,
            "description": "Exfiltration Over Alternative Protocol"
        },
        {
            "source_id": "MITRE-T1071",
            "target_id": "IP-MALICIOUS",
            "type": RelationshipType.MITRE_TECHNIQUE,
            "description": "Application Layer Protocol for C2"
        },
        {
            "source_id": "MITRE-T1068",
            "target_id": "SRV-001",
            "type": RelationshipType.MITRE_TECHNIQUE,
            "description": "Exploitation for Privilege Escalation"
        }
    ]
    
    return relationships

def seed_relationships():
    """Seed Neo4j with sample relationships"""
    
    rel_repo = RelationshipRepository()
    node_repo = NodeRepository()
    
    # First ensure nodes exist
    print("Checking nodes...")
    node_count = node_repo.count_nodes()
    if node_count == 0:
        print("No nodes found. Please run seed_nodes first.")
        return
    
    relationships = generate_relationships()
    
    created_count = 0
    for rel_data in relationships:
        try:
            # Create relationship
            rel = rel_repo.create_relationship(
                rel_data["source_id"],
                rel_data["target_id"],
                rel_data["type"],
                **{k: v for k, v in rel_data.items() if k not in ["source_id", "target_id", "type"]}
            )
            if rel:
                created_count += 1
                print(f"Created relationship: {rel_data['source_id']} - {rel_data['type']} -> {rel_data['target_id']}")
        except Exception as e:
            print(f"Error creating relationship {rel_data['source_id']} -> {rel_data['target_id']}: {e}")
    
    print(f"Seeded {created_count} of {len(relationships)} relationships")
    
    # Get statistics
    stats = rel_repo.get_relationship_statistics()
    print(f"Relationship statistics: {stats}")
    
    return relationships

if __name__ == "__main__":
    seed_relationships()