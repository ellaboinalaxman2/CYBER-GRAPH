# Cyber Graph — Frontend (Member 1)

> **"How does a security analyst see, understand, and interact with everything happening inside Cyber Graph?"**

Member 1 develops the **Cyber Graph Frontend** providing the security dashboard, interactive network graph, alerts, attack paths, AI predictions, event exploration, blockchain verification, and all user interactions by consuming APIs provided by Member 7 backend.

---

## ⚡ Quick Start

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies (already installed)
npm install

# 3. Start development server
npm run dev

# 4. Run test suite
npm test

# 5. Production build
npm run build
```

---

## 📂 Project Architecture

```
frontend/
├── README.md
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── .env
├── .env.example
│
├── public/
│   ├── logo.svg
│   └── favicon.ico
│
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css
│   │
│   ├── components/
│   │   ├── common/        (Button, Modal, Loader, ErrorMessage, EmptyState, Badge)
│   │   ├── layout/        (Navbar, Sidebar, Header, Footer, PageContainer)
│   │   ├── dashboard/     (StatsCard, ThreatOverview, EventTimeline, ThreatChart, AttackSummary, RecentAlerts)
│   │   ├── graph/         (CyberGraph, GraphNode, GraphEdge, GraphControls, GraphLegend, NodeDetails, GraphFilters, AttackPath)
│   │   ├── alerts/        (AlertCard, AlertList, AlertDetails, AlertSeverity, AlertFilters)
│   │   ├── attacks/       (AttackCard, AttackDetails, AttackTimeline, AttackPath, RiskScore, MitreTechnique)
│   │   ├── ai/            (AnomalyScore, PredictionCard, ConfidenceScore, AIExplanation, ModelStatus)
│   │   ├── blockchain/    (VerificationStatus, IntegrityBadge, TransactionDetails, AuditTrail)
│   │   ├── events/        (EventTable, EventDetails, EventFilters, EventTimeline)
│   │   └── search/        (SearchBar, SearchResults, SearchFilters)
│   │
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── CyberGraph.jsx
│   │   ├── Alerts.jsx
│   │   ├── Attacks.jsx
│   │   ├── AttackDetails.jsx
│   │   ├── Events.jsx
│   │   ├── NodeDetails.jsx
│   │   ├── BlockchainAudit.jsx
│   │   ├── Settings.jsx
│   │   └── NotFound.jsx
│   │
│   ├── services/          (api.js, authApi.js, graphApi.js, eventApi.js, alertApi.js, attackApi.js, aiApi.js, blockchainApi.js, mockData.js)
│   ├── hooks/             (useAuth.js, useGraph.js, useEvents.js, useAlerts.js, useAttacks.js, useAI.js, useBlockchain.js)
│   ├── context/           (AuthContext.jsx, GraphContext.jsx, AppContext.jsx)
│   ├── store/             (authStore.js, graphStore.js, alertStore.js, appStore.js)
│   ├── routes/            (AppRoutes.jsx, ProtectedRoute.jsx, PublicRoute.jsx)
│   ├── utils/             (formatters.js, dateUtils.js, graphUtils.js, severityUtils.js, validators.js)
│   ├── constants/         (routes.js, severity.js, nodeTypes.js, eventTypes.js)
│   └── styles/            (globals.css, dashboard.css, graph.css, responsive.css)
│
├── tests/
│   ├── components/
│   ├── services/
│   └── utils/
│
└── docs/
    ├── architecture.md
    ├── ui-design.md
    ├── graph-visualization.md
    ├── api-integration.md
    └── components.md
```

---

## 🔒 Security Principles
- All internal backend credentials (Neo4j, MongoDB, blockchain private keys, JWT secrets) are **never** present on the frontend or `.env`.
- Frontend safely consumes HTTP endpoints exposed exclusively by Member 7 Backend API.
