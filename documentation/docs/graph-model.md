# Graph Model Documentation

## Overview

The Cyber Graph uses Neo4j to represent network topology, device relationships, and attack paths.

## Node Types

### 1. DEVICE
Generic device representation.

```cypher
(:DEVICE {
    id: "DEV-001",
    type: "DEVICE",
    name: "Device-01",
    hostname: "device-01",
    ip_address: "192.168.1.5",
    status: "active",
    criticality: 3,
    description: "Device description",
    created_at: "2026-08-29T10:00:00Z",
    updated_at: "2026-08-29T10:00:00Z"
})