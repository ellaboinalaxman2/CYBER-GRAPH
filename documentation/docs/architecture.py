# Cyber Graph Database Architecture

## Overview

Cyber Graph uses a dual-database architecture to handle different types of data effectively:

- **MongoDB**: Document-oriented storage for events, alerts, users, incidents, and audit logs
- **Neo4j**: Graph database for network topology, relationships, and attack path analysis

## Why Two Databases?

### MongoDB vs Neo4j

| Data Type | MongoDB | Neo4j |
|-----------|---------|-------|
| Security Events | ✓ | Reference only |
| Alerts | ✓ | Optional nodes |
| Users | ✓ | Can be graph nodes |
| Incident Metadata | ✓ | Optional |
| Network Relationships | ✓ | ✓ |
| Attack Paths | ✓ | ✓ |
| Graph Traversal | Limited | ✓ |
| Event Documents | ✓ | ✓ |

## Data Flow
Member 2 (Data Processing) → Member 4 (Database)
↓
MongoDB (Events/Alerts)
↓
Neo4j (Graph/Topology)
↓
Member 3 (AI), Member 5 (Attack), Member 6 (Blockchain)
↓
Member 7 (Backend API)