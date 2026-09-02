# Cyber Graph — Component Reference

## Component Inventory

### 1. Common Components (`src/components/common/`)
- `Button.jsx`: Styled cyberpunk action button with multiple variants and loading states.
- `Modal.jsx`: Accessible modal dialog for detailed analysis.
- `Loader.jsx`: Spinning radar cyber loader.
- `ErrorMessage.jsx`: Error boundary / connection retry card.
- `EmptyState.jsx`: Zero-state shield indicator.
- `Badge.jsx`: Severity & status tag badge with pulsating dots.

### 2. Layout Components (`src/components/layout/`)
- `Navbar.jsx` / `Header.jsx`: Top navigation with global telemetry search, health status, and alert drop-down.
- `Sidebar.jsx`: Collapsible SOC navigation bar.
- `Footer.jsx`: System integration status bar.
- `PageContainer.jsx`: Responsive layout wrapper with title and breadcrumb headers.

### 3. Dashboard (`src/components/dashboard/`)
- `StatsCard.jsx`: Metric cards for Assets, Alerts, Attacks, and Critical Threats.
- `ThreatOverview.jsx`: Security posture assessment card.
- `ThreatChart.jsx`: 24-hour event timeline vs anomaly area chart.
- `RecentAlerts.jsx`: Real-time triaged alert feed.
- `AttackSummary.jsx`: Attack campaigns summary.

### 4. Graph Visualization (`src/components/graph/`)
- `CyberGraph.jsx`: Interactive Cytoscape network graph canvas.
- `GraphNode.jsx` & `GraphEdge.jsx`: Entity definitions.
- `GraphControls.jsx`: Zoom, fit, and layout switcher.
- `GraphLegend.jsx`: Topology color codes and relation types.
- `NodeDetails.jsx`: Node inspector drawer.
- `GraphFilters.jsx`: Filter by node type, severity, and search.
- `AttackPath.jsx`: Multi-hop attack path stepper.

### 5. Alerts, Attacks, AI, Blockchain, Events
- `AlertCard.jsx`, `AlertList.jsx`, `AlertDetails.jsx`, `AlertSeverity.jsx`, `AlertFilters.jsx`
- `AttackCard.jsx`, `AttackDetails.jsx`, `AttackTimeline.jsx`, `RiskScore.jsx`, `MitreTechnique.jsx`
- `AnomalyScore.jsx`, `PredictionCard.jsx`, `ConfidenceScore.jsx`, `AIExplanation.jsx`, `ModelStatus.jsx`
- `VerificationStatus.jsx`, `IntegrityBadge.jsx`, `TransactionDetails.jsx`, `AuditTrail.jsx`
- `EventTable.jsx`, `EventDetails.jsx`, `EventFilters.jsx`, `EventTimeline.jsx`
- `SearchBar.jsx`, `SearchResults.jsx`, `SearchFilters.jsx`
