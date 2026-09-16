from typing import List, Dict, Any
from ..models.node_types import NodeType
from ..repositories.node_repository import NodeRepository

def generate_nodes() -> List[Dict[str, Any]]:
    """Generate sample nodes for testing"""
    
    nodes = [
        # Workstations
        {
            "type": NodeType.WORKSTATION,
            "id": "WS-001",
            "name": "Workstation-01",
            "hostname": "employee-pc-01",
            "ip_address": "192.168.1.5",
            "os": "Windows 10",
            "os_version": "22H2",
            "status": "active",
            "criticality": 2,
            "description": "Employee workstation - Finance Department",
            "user": "john.doe",
            "department": "Finance",
            "software": ["Office 365", "Chrome", "Slack"]
        },
        {
            "type": NodeType.WORKSTATION,
            "id": "WS-002",
            "name": "Workstation-02",
            "hostname": "employee-pc-02",
            "ip_address": "192.168.1.6",
            "os": "Windows 10",
            "os_version": "22H2",
            "status": "active",
            "criticality": 2,
            "description": "Employee workstation - HR Department",
            "user": "jane.smith",
            "department": "HR",
            "software": ["Office 365", "Chrome", "Workday"]
        },
        {
            "type": NodeType.WORKSTATION,
            "id": "WS-003",
            "name": "Workstation-03",
            "hostname": "developer-pc-01",
            "ip_address": "192.168.1.7",
            "os": "Ubuntu 22.04",
            "os_version": "22.04 LTS",
            "status": "active",
            "criticality": 3,
            "description": "Developer workstation",
            "user": "alex.dev",
            "department": "Engineering",
            "software": ["VS Code", "Docker", "Git", "Python", "Node.js"]
        },
        
        # Servers
        {
            "type": NodeType.APPLICATION_SERVER,
            "id": "SRV-001",
            "name": "App-Server-01",
            "hostname": "app-server-01",
            "ip_address": "192.168.1.10",
            "os": "Ubuntu 22.04",
            "os_version": "22.04 LTS",
            "status": "active",
            "criticality": 4,
            "description": "Primary application server",
            "server_role": "Application Server",
            "services": ["Tomcat", "Nginx", "PostgreSQL Client"],
            "ports": [80, 443, 8080, 5432],
            "cpu_cores": 8,
            "memory_gb": 32,
            "storage_gb": 500
        },
        {
            "type": NodeType.WEB_SERVER,
            "id": "SRV-002",
            "name": "Web-Server-01",
            "hostname": "web-server-01",
            "ip_address": "192.168.1.11",
            "os": "Ubuntu 22.04",
            "os_version": "22.04 LTS",
            "status": "active",
            "criticality": 3,
            "description": "Web server hosting company website",
            "server_role": "Web Server",
            "services": ["Apache", "PHP-FPM"],
            "ports": [80, 443],
            "cpu_cores": 4,
            "memory_gb": 16,
            "storage_gb": 100
        },
        {
            "type": NodeType.FILE_SERVER,
            "id": "SRV-003",
            "name": "File-Server-01",
            "hostname": "file-server-01",
            "ip_address": "192.168.1.12",
            "os": "Windows Server 2022",
            "os_version": "2022",
            "status": "active",
            "criticality": 3,
            "description": "File server for department shares",
            "server_role": "File Server",
            "services": ["SMB", "DFS"],
            "ports": [445, 139],
            "cpu_cores": 4,
            "memory_gb": 16,
            "storage_gb": 1000
        },
        {
            "type": NodeType.EMAIL_SERVER,
            "id": "SRV-004",
            "name": "Email-Server-01",
            "hostname": "email-server-01",
            "ip_address": "192.168.1.13",
            "os": "Ubuntu 22.04",
            "os_version": "22.04 LTS",
            "status": "active",
            "criticality": 4,
            "description": "Email server",
            "server_role": "Email Server",
            "services": ["Postfix", "Dovecot", "SpamAssassin"],
            "ports": [25, 587, 993, 143],
            "cpu_cores": 4,
            "memory_gb": 16,
            "storage_gb": 200
        },
        
        # Databases
        {
            "type": NodeType.DATABASE,
            "id": "DB-001",
            "name": "Database-01",
            "hostname": "db-server-01",
            "ip_address": "192.168.1.20",
            "os": "Ubuntu 22.04",
            "os_version": "22.04 LTS",
            "status": "active",
            "criticality": 5,
            "description": "Primary database server",
            "db_type": "PostgreSQL",
            "db_version": "15.2",
            "tables": 45,
            "size_gb": 200,
            "sensitive_data": True
        },
        {
            "type": NodeType.DATABASE,
            "id": "DB-002",
            "name": "Database-02",
            "hostname": "db-server-02",
            "ip_address": "192.168.1.21",
            "os": "Ubuntu 22.04",
            "os_version": "22.04 LTS",
            "status": "active",
            "criticality": 4,
            "description": "Analytics database",
            "db_type": "MySQL",
            "db_version": "8.0",
            "tables": 30,
            "size_gb": 100,
            "sensitive_data": False
        },
        
        # Network Devices
        {
            "type": NodeType.FIREWALL,
            "id": "FW-001",
            "name": "Firewall-01",
            "hostname": "firewall-01",
            "ip_address": "192.168.1.1",
            "os": "Palo Alto PAN-OS",
            "os_version": "10.2",
            "status": "active",
            "criticality": 5,
            "description": "Primary network firewall"
        },
        {
            "type": NodeType.ROUTER,
            "id": "RT-001",
            "name": "Router-01",
            "hostname": "router-01",
            "ip_address": "192.168.1.254",
            "os": "Cisco IOS",
            "os_version": "15.6",
            "status": "active",
            "criticality": 4,
            "description": "Core network router"
        },
        {
            "type": NodeType.SWITCH,
            "id": "SW-001",
            "name": "Switch-01",
            "hostname": "switch-01",
            "ip_address": "192.168.1.2",
            "os": "Cisco IOS",
            "os_version": "15.2",
            "status": "active",
            "criticality": 3,
            "description": "Access switch"
        },
        
        # Security Nodes (for attack simulation)
        {
            "type": NodeType.IP_ADDRESS,
            "id": "IP-MALICIOUS",
            "name": "Malicious IP",
            "hostname": "attacker-c2",
            "ip_address": "45.33.22.11",
            "status": "active",
            "criticality": 5,
            "description": "Known malicious C2 server"
        },
        {
            "type": NodeType.MITRE_TECHNIQUE,
            "id": "MITRE-T1021",
            "name": "Lateral Movement",
            "technique_id": "T1021",
            "description": "Remote Services - Lateral Movement",
            "criticality": 4
        },
        {
            "type": NodeType.MITRE_TECHNIQUE,
            "id": "MITRE-T1048",
            "name": "Exfiltration",
            "technique_id": "T1048",
            "description": "Exfiltration Over Alternative Protocol",
            "criticality": 5
        },
        {
            "type": NodeType.MITRE_TECHNIQUE,
            "id": "MITRE-T1071",
            "name": "C2 Communication",
            "technique_id": "T1071",
            "description": "Application Layer Protocol - C2",
            "criticality": 4
        },
        {
            "type": NodeType.MITRE_TECHNIQUE,
            "id": "MITRE-T1068",
            "name": "Privilege Escalation",
            "technique_id": "T1068",
            "description": "Exploitation for Privilege Escalation",
            "criticality": 5
        }
    ]
    
    return nodes

def seed_nodes():
    """Seed Neo4j with sample nodes"""
    
    node_repo = NodeRepository()
    
    # Clear existing nodes
    node_repo.clear_graph()
    print("Cleared existing graph")
    
    nodes = generate_nodes()
    
    for node_data in nodes:
        # Extract type and create node
        node_type = node_data.pop("type")
        node = node_repo.create_node(node_type, **node_data)
        if node:
            print(f"Created node: {node.get('id')} ({node.get('type')})")
    
    print(f"Seeded {len(nodes)} nodes")
    
    # Get statistics
    stats = node_repo.get_node_statistics()
    print(f"Graph statistics: {stats}")
    
    return nodes

if __name__ == "__main__":
    seed_nodes()