# Cyber Graph - Attack Engine (Member 5)

## Overview

Member 5 is the Attack Engine for Cyber Graph. It:

- Correlates security events
- Reconstructs attack paths
- Assesses risk
- Maps to MITRE ATT&CK
- Generates security alerts

## Features

### Phase 1: Foundation & Event Correlation ✅

- Event correlation rules
- Temporal correlation
- Behavioral correlation
- Incident creation

### Phase 2: Attack Path Reconstruction ✅

- Graph traversal
- Path building
- Attack reconstruction
- Sequence analysis

### Phase 3: Risk Assessment ✅

- Risk scoring
- Severity calculation
- Asset criticality
- Risk rules

### Phase 4: MITRE ATT&CK Mapping ✅

- Technique mapping
- Tactic mapping
- Attack mapping
- Confidence scoring

### Phase 5: Alert Generation ✅

- Alert classification
- Alert formatting
- Alert generation
- Status management

### Phase 6: API & Integration ✅

- REST API with rate limiting
- Integration with Members 2, 3, 4, 6
- Security middleware
- Production ready

## Quick Start

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Seed MITRE data
python scripts/seed_mitre.py

# Start the server
python run.py
```
