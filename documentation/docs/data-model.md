# Data Model Documentation

## MongoDB Data Models

### 1. Event Model

**Purpose**: Stores security events produced by Member 2

```json
{
    "event_id": "EVT-001",
    "timestamp": "2026-08-29T10:30:00Z",
    "source": "192.168.1.5",
    "source_port": 22,
    "destination": "192.168.1.10",
    "destination_port": 443,
    "protocol": "SSH",
    "event_type": "NETWORK_CONNECTION",
    "user": "john.doe",
    "process": "sshd",
    "command_line": "/usr/sbin/sshd -D",
    "message": "SSH connection established",
    "severity": "INFO",
    "raw_log": "sshd[1234]: Accepted password for john.doe",
    "normalized_data": {},
    "tags": ["network", "ssh"],
    "is_anomaly": false,
    "anomaly_score": 0.05,
    "source_hostname": "PC-01",
    "destination_hostname": "Server-01",
    "bytes_sent": 1024,
    "bytes_received": 2048,
    "duration": 3600.5,
    "country": "US",
    "metadata": {},
    "processed_at": "2026-08-29T10:30:05Z",
    "ingestion_timestamp": "2026-08-29T10:30:10Z",
    "source_type": "NETWORK"
}