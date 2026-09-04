````markdown
# 🛡️ CYBER-GRAPH

### AI-Powered Cyber Attack Detection and Attack Path Reconstruction

CYBER-GRAPH is an AI-powered cybersecurity system that detects suspicious network activity, identifies relationships between devices, reconstructs the probable path of an attack, calculates risk, maps attacks to MITRE ATT&CK techniques, and maintains a tamper-evident security audit trail using blockchain.

---

## 🚨 Problem

Traditional cybersecurity systems usually generate individual alerts.

For example:

- PC-01 has a failed login
- Server-01 receives an unusual SSH connection
- Server-02 shows suspicious activity
- Database-01 is accessed unexpectedly

Individually, these events may not look dangerous.

However, when these events are connected, they may represent a complete attack:

```text
PC-01
  ↓
Server-01
  ↓
Server-02
  ↓
Database
````

The main problem is that security analysts have to manually correlate these events and understand how the attack moved through the network.

CYBER-GRAPH automates this process.

---

# 💡 Solution

CYBER-GRAPH represents cybersecurity events and devices as a graph.

It uses:

* **GraphSAGE** for AI-based anomaly detection
* **MongoDB** for storing security events
* **Neo4j** for storing device relationships
* **Attack Path Reconstruction** to identify probable attack chains
* **Risk Engine** to calculate incident severity
* **MITRE ATT&CK** to identify attack techniques
* **Blockchain** to maintain tamper-evident security records
* **FastAPI** as the backend
* **React** for the dashboard

---

# 🔄 How CYBER-GRAPH Works

The complete system works as follows:

```text
Security Logs / CICIDS2017
          ↓
   Data Collection
          ↓
   Data Preprocessing
          ↓
   ┌───────────────┐
   │    MongoDB    │
   │ Event Storage │
   └───────────────┘
          ↓
     Graph Builder
          ↓
      Neo4j Graph
          ↓
       GraphSAGE
          ↓
   Anomaly Detection
          ↓
    Event Correlation
          ↓
 Attack Path Reconstruction
          ↓
      Risk Engine
       ↙       ↘
 MITRE ATT&CK  Blockchain
       ↘       ↙
        FastAPI
          ↓
    React Dashboard
          ↓
   Security Analyst
```

---

# 🧠 AI-Based Detection

CYBER-GRAPH uses **GraphSAGE (Graph Sample and Aggregate)** for graph-based anomaly detection.

GraphSAGE learns representations of devices using:

* Node features
* Neighboring nodes
* Relationships between nodes

This is useful in cybersecurity because attacks usually involve multiple connected systems rather than a single isolated event.

### GraphSAGE Pipeline

```text
Network Events
      ↓
     Graph
      ↓
 Node Features
      ↓
   GraphSAGE
      ↓
  Embeddings
      ↓
  Classifier
      ↓
  Prediction
```

Example:

```text
Server-01

Anomaly Score: 0.94
Prediction: ATTACK
```

---

# 📊 Dataset

The initial development and evaluation uses the **CICIDS2017** cybersecurity dataset.

It contains normal and malicious network traffic.

Example attack categories include:

* BENIGN
* Brute Force
* DoS
* DDoS
* Port Scan
* Bot
* Web Attacks
* Infiltration

The dataset is used to train and evaluate the AI detection system.

---

# 🗄️ MongoDB

MongoDB is used to store cybersecurity events.

Example:

```json
{
  "event_id": "EVT-001",
  "source": "192.168.1.5",
  "destination": "192.168.1.10",
  "protocol": "SSH",
  "timestamp": "2026-05-13T10:30:00",
  "attack_type": "SSH-Patator"
}
```

MongoDB stores information about **what happened**.

---

# 🕸️ Neo4j Graph Database

Neo4j stores relationships between devices and events.

For example:

```text
PC-01
  │
  ▼
Server-01
  │
  ▼
Server-02
  │
  ▼
DB-01
```

This allows CYBER-GRAPH to understand **how systems are connected**.

NetworkX can also be used for graph processing and algorithms on the Python side.

---

# 🔗 Event Correlation

Multiple suspicious events are correlated to determine whether they belong to the same incident.

For example:

```text
Failed Login
     ↓
Suspicious SSH Connection
     ↓
Internal Server Access
     ↓
Lateral Movement
     ↓
Database Access
```

Instead of showing five unrelated alerts, CYBER-GRAPH can identify them as part of a possible attack chain.

---

# 🛣️ Attack Path Reconstruction

After detecting suspicious activity, the system analyzes graph relationships and correlated events.

Example:

```text
PC-01
  ↓
Server-01
  ↓
Server-02
  ↓
DB-01
```

The system identifies this as the **probable attack path**.

This helps security analysts understand:

* Where the attack started
* Which systems were involved
* How the attacker moved
* Which critical systems may be at risk

---

# ⚠️ Risk Engine

Each detected incident receives a risk score.

The risk is based on factors such as:

```text
AI Anomaly Score
        +
Asset Criticality
        +
Attack Severity
        +
Behavioral Evidence
        ↓
    Risk Score
```

Example:

```text
Risk Score: 94/100
Classification: CRITICAL
```

### Risk Levels

|  Score | Risk     |
| -----: | -------- |
|   0–30 | LOW      |
|  31–60 | MEDIUM   |
|  61–80 | HIGH     |
| 81–100 | CRITICAL |

These thresholds can be adjusted during testing.

---

# 🎯 MITRE ATT&CK Mapping

Detected behavior can be mapped to MITRE ATT&CK techniques.

Example:

```text
Brute Force
    ↓
T1110

SSH
    ↓
T1021.004
```

This gives security analysts a standardized way to understand the attack technique involved.

---

# 🔐 Blockchain Security

Blockchain is used to protect the integrity of important security records.

When an alert is generated:

```text
Alert Data
    ↓
 SHA-256
    ↓
   Hash
    ↓
Blockchain
```

If someone later modifies the stored alert, the system can calculate the hash again and compare it with the blockchain record.

If the hashes are different:

```text
🚨 INTEGRITY VIOLATION
```

### Blockchain provides:

* Tamper-evident audit trail
* Integrity verification
* Security event verification

### Blockchain does NOT:

* Detect attacks
* Replace GraphSAGE
* Replace MongoDB
* Reconstruct attack paths
* Automatically stop hackers

---

# ⚙️ Backend

The backend is built using **FastAPI and Python**.

The backend connects:

```text
React
  ↓
FastAPI
  ↓
MongoDB
Neo4j
GraphSAGE
Blockchain
```

Example APIs:

```text
GET /api/events
GET /api/nodes
GET /api/alerts
GET /api/attack-path/{id}
GET /api/risk/{id}
GET /api/statistics
GET /api/blockchain/verify/{id}
```

---

# 🔑 Authentication

The system uses **JWT authentication**.

Different user roles can be supported:

```text
Admin
  → Full access

Analyst
  → Investigate alerts

Viewer
  → View dashboard
```

---

# 🖥️ Frontend

The dashboard is built using:

* React
* JavaScript
* Tailwind CSS
* Cytoscape.js

The dashboard allows analysts to visualize:

* Network devices
* Suspicious events
* Attack paths
* Risk scores
* MITRE ATT&CK techniques
* Security alerts
* Blockchain verification status

Example:

```text
🔴 CRITICAL ATTACK DETECTED

Attack Type: Lateral Movement
Risk Score: 94/100

Attack Path:

PC-01
  ↓
Server-01
  ↓
Server-02
  ↓
Database

MITRE ATT&CK:
T1110 - Brute Force
T1021.004 - SSH

Blockchain Integrity: ✅ VERIFIED
```

---

# 🛠️ Technology Stack

| Category            | Technology                   |
| ------------------- | ---------------------------- |
| Frontend            | React                        |
| Styling             | Tailwind CSS                 |
| Graph Visualization | Cytoscape.js                 |
| Backend             | FastAPI                      |
| Programming         | Python, JavaScript           |
| Database            | MongoDB                      |
| Graph Database      | Neo4j                        |
| Graph Processing    | NetworkX                     |
| Machine Learning    | PyTorch, Scikit-learn        |
| GNN                 | PyTorch Geometric, GraphSAGE |
| Data Processing     | Pandas, NumPy                |
| Dataset             | CICIDS2017                   |
| Security Framework  | MITRE ATT&CK                 |
| Authentication      | JWT                          |
| Audit / Integrity   | Blockchain                   |
| Containerization    | Docker                       |
| Version Control     | Git, GitHub                  |

---

# 📁 Project Structure

```text
CYBER-GRAPH/
│
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── database/
│   ├── graph/
│   ├── ml/
│   ├── risk_engine/
│   ├── blockchain/
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
├── dataset/
│   └── CICIDS2017/
│
├── models/
│   └── graphsage/
│
├── docker/
│
├── README.md
└── .gitignore
```

---

# 🚀 Main Features

### 1. AI Attack Detection

Detects suspicious network behavior using GraphSAGE.

### 2. Graph-Based Security Analysis

Represents devices and their relationships as a graph.

### 3. Event Correlation

Connects multiple security events into meaningful incidents.

### 4. Attack Path Reconstruction

Identifies the probable path followed during an attack.

### 5. Risk Assessment

Assigns a risk score to each incident.

### 6. MITRE ATT&CK Mapping

Maps detected behavior to known attack techniques.

### 7. Blockchain Audit

Provides tamper-evident verification of important security records.

### 8. Security Dashboard

Provides analysts with a visual representation of attacks, devices, paths and risks.

---

# 🌟 What Makes CYBER-GRAPH Different?

Traditional IDS:

```text
Attack
  ↓
"Attack Detected"
```

CYBER-GRAPH:

```text
Attack
  ↓
Detect Suspicious Activity
  ↓
Correlate Events
  ↓
Build Security Graph
  ↓
Reconstruct Attack Path
  ↓
Calculate Risk
  ↓
Map MITRE ATT&CK
  ↓
Verify Security Record
  ↓
Show Complete Incident
```

The main contribution of CYBER-GRAPH is the **combination of graph-based AI, attack-path reconstruction, risk analysis, MITRE ATT&CK mapping, and blockchain-based audit integrity**.

---

# 🎯 Project Goal

The goal of CYBER-GRAPH is to help security analysts move from simply knowing that an attack occurred to understanding:

```text
WHAT happened?
        ↓
WHERE did it happen?
        ↓
HOW did the attack move?
        ↓
WHAT systems are at risk?
        ↓
WHAT technique was used?
        ↓
CAN the incident record be trusted?
```

---

# 📌 Project Status

🚧 Currently under development.

The initial version focuses on:

* CICIDS2017-based detection
* Graph construction
* GraphSAGE anomaly detection
* Event correlation
* Attack-path reconstruction
* Risk scoring
* MITRE ATT&CK mapping
* Blockchain-based integrity verification
* FastAPI backend
* React dashboard

---

# 👨‍💻 Team

Developed as a cybersecurity and AI project.

**CYBER-GRAPH**

> Turning security events into an understandable attack story.

```

This version is intentionally **basic and readable**: someone opening your GitHub repository can understand the **entire project from top to bottom without being overwhelmed by implementation details**. It also follows the actual architecture and features in your project document rather than adding unrelated functionality.

If you want, I can also make a **more professional “top GitHub repository” version** with badges, screenshots section, demo section, installation commands, and a polished architecture diagram.
```
