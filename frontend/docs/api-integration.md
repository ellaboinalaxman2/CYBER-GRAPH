# Cyber Graph — API Integration Specification

## 1. REST Endpoint Contract with Member 7 (Backend)

The frontend communicates with Member 7 via Axios configured in `src/services/api.js`:

| Endpoint | Method | Response Payload | Description |
| :--- | :--- | :--- | :--- |
| `/api/auth/login` | POST | `{ token, user }` | Authenticate security analyst |
| `/api/auth/me` | GET | `{ user }` | Validate active session token |
| `/api/graph` | GET | `{ nodes: [], edges: [] }` | Fetch complete network topology |
| `/api/graph/node/:id` | GET | `{ id, type, ip, risk, anomaly_score, ... }` | Inspect specific node asset |
| `/api/alerts` | GET | `{ alerts: [], total }` | Fetch triaged security alerts |
| `/api/alerts/:id/status` | PUT | `{ success: true, status }` | Update alert resolution status |
| `/api/attacks` | GET | `[ { id, title, riskScore, mitre, path, ... } ]` | Multi-stage attack campaigns |
| `/api/events` | GET | `{ events: [], total }` | Normalized event stream |
| `/api/ai/prediction/:id` | GET | `{ prediction, anomaly_score, confidence, explanations }` | GraphSAGE GNN inference |
| `/api/blockchain/verify/:id`| GET | `{ verified, transaction_hash, block_number, timestamp }` | Proof-of-Authority verification |

## 2. Mock Fallback Mode
If Member 7 backend is offline or during standalone local testing, `ENABLE_MOCK_FALLBACK=true` returns structured mock data automatically.
