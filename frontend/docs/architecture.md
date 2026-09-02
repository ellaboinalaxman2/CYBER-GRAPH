# Cyber Graph — Member 1 (Frontend) Architecture

## 1. Executive Summary
Member 1 is responsible for the entire user interface and security analyst experience of the **Cyber Graph** autonomous SOC defense platform. The frontend enables security analysts to visualize complex relationships between network assets, trace multi-hop attack campaigns, review AI GraphSAGE anomaly detections, audit cryptographic blockchain event proofs, and manage active incident alerts.

## 2. 7-Member Team Topology

```
                  ┌───────────────────────────────┐
                  │          CYBER GRAPH          │
                  └───────────────┬───────────────┘
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      │                           │                           │
      ▼                           ▼                           ▼
  MEMBER 1                    MEMBER 2                    MEMBER 3
  FRONTEND                    INGESTION                   AI ENGINE
  (Show It)                  (Collect It)                (Detect It)
      │                           │                           │
      │ HTTP                      │                           ▼
      ▼                           │                       GraphSAGE
  MEMBER 7 ◄──────────────────────┤                        Anomalies
  BACKEND                         │
  (Connect It)                    ▼
      │                       MEMBER 4
      │                       DATABASE
      │                       (Store It: Neo4j / MongoDB)
      │                           │
      ├───────────────────────────┤
      ▼                           ▼
  MEMBER 5                    MEMBER 6
  ATTACK ENGINE               BLOCKCHAIN
  (Understand It)             (Prove It)
```

## 3. Tech Stack
- **Framework**: React 18 / Vite
- **Styling**: Tailwind CSS (Dark Cyber Theme)
- **Graph Engine**: Cytoscape.js
- **Charts & Telemetry**: Recharts
- **Icons**: Lucide React
- **Routing**: React Router DOM (v6) with Protected Session guards
- **HTTP Client**: Axios with fallback mock interceptor
- **Testing**: Vitest + React Testing Library
