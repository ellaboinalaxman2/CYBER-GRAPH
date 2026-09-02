# Cyber Graph - Database Engine (Member 4)

## Overview

Member 4 is the Database & Graph Engine for Cyber Graph. It manages:

- **MongoDB**: Document storage for events, alerts, and incidents
- **Neo4j**: Graph storage for network relationships and attack paths

## Features

### Phase 1: Foundation & MongoDB Setup ✅

- MongoDB connection with connection pooling
- Event CRUD operations
- Index management
- REST API for events

### Phase 2: Neo4j Graph Setup ✅

- Neo4j connection with connection pooling
- Node and relationship management
- Path finding and graph traversal
- Graph statistics and attack paths

### Phase 3: Advanced Features ✅

- Alert management (CRUD, status, assignment)
- Incident management (CRUD, status tracking)
- Data migrations
- Backup & recovery

### Phase 4: API & Integration ✅

- Rate limiting
- Security headers
- Integration with Members 2, 3, 5
- API documentation
- Production readiness

## Quick Start

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start MongoDB and Neo4j
# Then start the server
python run.py
```
