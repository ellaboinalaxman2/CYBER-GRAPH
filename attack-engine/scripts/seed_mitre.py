"""Script to seed MITRE ATT&CK data."""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.logging import setup_logging, get_logger


def main():
    """Seed MITRE data."""
    setup_logging()
    logger = get_logger("scripts.seed_mitre")
    
    # MITRE data path
    mitre_path = Path(settings.mitre_data_path)
    mitre_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load data from file or create default
    if mitre_path.exists():
        with open(mitre_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded existing MITRE data from {mitre_path}")
    else:
        # Create default MITRE data
        data = {
            "techniques": [
                {
                    "id": "T1110",
                    "name": "Brute Force",
                    "tactics": ["Credential Access"],
                    "description": "Adversaries may use brute force techniques to gain access to accounts.",
                    "subtechniques": [
                        {"id": "T1110.001", "name": "Password Guessing"},
                        {"id": "T1110.002", "name": "Password Cracking"},
                        {"id": "T1110.003", "name": "Password Spraying"}
                    ]
                },
                {
                    "id": "T1078",
                    "name": "Valid Accounts",
                    "tactics": ["Defense Evasion", "Persistence", "Privilege Escalation", "Initial Access"],
                    "description": "Adversaries may obtain and abuse credentials of existing accounts.",
                    "subtechniques": [
                        {"id": "T1078.001", "name": "Default Accounts"},
                        {"id": "T1078.002", "name": "Domain Accounts"},
                        {"id": "T1078.003", "name": "Local Accounts"}
                    ]
                },
                {
                    "id": "T1021",
                    "name": "Remote Services",
                    "tactics": ["Lateral Movement"],
                    "description": "Adversaries may use remote services to move laterally.",
                    "subtechniques": [
                        {"id": "T1021.001", "name": "Remote Desktop Protocol"},
                        {"id": "T1021.002", "name": "SMB/Windows Admin Shares"},
                        {"id": "T1021.004", "name": "SSH"},
                        {"id": "T1021.006", "name": "WinRM"}
                    ]
                },
                {
                    "id": "T1133",
                    "name": "External Remote Services",
                    "tactics": ["Initial Access", "Persistence"],
                    "description": "Adversaries may leverage external remote services to gain initial access."
                },
                {
                    "id": "T1190",
                    "name": "Exploit Public-Facing Application",
                    "tactics": ["Initial Access"],
                    "description": "Adversaries may exploit vulnerabilities in public-facing applications."
                },
                {
                    "id": "T1046",
                    "name": "Network Service Scanning",
                    "tactics": ["Discovery"],
                    "description": "Adversaries may scan for network services to discover targets."
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "tactics": ["Execution"],
                    "description": "Adversaries may abuse command and script interpreters.",
                    "subtechniques": [
                        {"id": "T1059.001", "name": "PowerShell"},
                        {"id": "T1059.003", "name": "Windows Command Shell"},
                        {"id": "T1059.004", "name": "Unix Shell"}
                    ]
                },
                {
                    "id": "T1068",
                    "name": "Exploitation for Privilege Escalation",
                    "tactics": ["Privilege Escalation"],
                    "description": "Adversaries may exploit vulnerabilities to escalate privileges."
                },
                {
                    "id": "T1083",
                    "name": "File and Directory Discovery",
                    "tactics": ["Discovery"],
                    "description": "Adversaries may enumerate files and directories."
                },
                {
                    "id": "T1003",
                    "name": "OS Credential Dumping",
                    "tactics": ["Credential Access"],
                    "description": "Adversaries may dump credentials from the operating system."
                },
                {
                    "id": "T1562",
                    "name": "Impair Defenses",
                    "tactics": ["Defense Evasion"],
                    "description": "Adversaries may disable or impair security defenses.",
                    "subtechniques": [
                        {"id": "T1562.001", "name": "Disable or Modify Tools"},
                        {"id": "T1562.002", "name": "Disable Windows Event Logging"},
                        {"id": "T1562.004", "name": "Disable or Modify System Firewall"}
                    ]
                },
                {
                    "id": "T1486",
                    "name": "Data Encrypted for Impact",
                    "tactics": ["Impact"],
                    "description": "Adversaries may encrypt data to impact availability."
                },
                {
                    "id": "T1498",
                    "name": "Network Denial of Service",
                    "tactics": ["Impact"],
                    "description": "Adversaries may perform network denial of service attacks.",
                    "subtechniques": [
                        {"id": "T1498.001", "name": "Direct Network Flood"},
                        {"id": "T1498.002", "name": "Reflection Amplification"}
                    ]
                },
                {
                    "id": "T1550",
                    "name": "Use Alternate Authentication Material",
                    "tactics": ["Defense Evasion", "Lateral Movement"],
                    "description": "Adversaries may use alternate authentication materials.",
                    "subtechniques": [
                        {"id": "T1550.001", "name": "Application Access Token"},
                        {"id": "T1550.002", "name": "Pass the Hash"},
                        {"id": "T1550.003", "name": "Pass the Ticket"}
                    ]
                }
            ],
            "tactics": [
                "Reconnaissance",
                "Resource Development",
                "Initial Access",
                "Execution",
                "Persistence",
                "Privilege Escalation",
                "Defense Evasion",
                "Credential Access",
                "Discovery",
                "Lateral Movement",
                "Collection",
                "Command and Control",
                "Exfiltration",
                "Impact"
            ],
            "version": "14.1",
            "last_updated": "2026-09-01T00:00:00Z"
        }
        
        with open(mitre_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Created default MITRE data at {mitre_path}")
    
    logger.info(f"MITRE data seeded with {len(data.get('techniques', []))} techniques")
    logger.info(f"  - Version: {data.get('version', 'unknown')}")
    logger.info(f"  - Tactics: {len(data.get('tactics', []))}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())