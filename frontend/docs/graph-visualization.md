# Cyber Graph — Graph Visualization Guide

## 1. Cytoscape.js Integration
The interactive relationship graph visualization is implemented in `CyberGraph.jsx` using `Cytoscape.js`.

### Supported Node Types:
- **PC / Workstation**: Cyan nodes (`#06b6d4`)
- **Server**: Purple nodes (`#8b5cf6`)
- **Database**: Pink nodes (`#ec4899`)
- **Router / Gateway**: Blue nodes (`#3b82f6`)
- **Firewall**: Orange nodes (`#f97316`)
- **User / Admin**: Emerald nodes (`#10b981`)
- **Compromised / Suspicious Nodes**: Red glowing nodes (`#ef4444`)

### Supported Relationship Types:
- `CONNECTS_TO`
- `ACCESSES`
- `AUTHENTICATES`
- `COMMUNICATES_WITH`

## 2. Attack Path Overlay
When an attack campaign is selected (e.g. `ATK-2026-001`), the graph highlights the malicious hop traversal sequence with glowing red animated edges, enlarging victim and perpetrator nodes, and providing step-by-step playback.
