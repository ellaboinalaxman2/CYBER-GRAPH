# Cyber Graph Backend

A FastAPI-based backend for cyber threat graph analysis and visualization.

## Features

- **Authentication**: JWT-based user authentication with role-based access control
- **Event Ingestion**: Real-time security event processing and storage
- **Graph Analysis**: Neo4j-based attack path analysis and visualization
- **Alert Management**: Security alert tracking and management
- **Blockchain Integration**: Immutable audit trail using blockchain technology
- **MITRE ATT&CK**: Integration with MITRE ATT&CK framework
- **Risk Assessment**: Automated risk scoring and analysis
- **Statistics**: Real-time statistics and reporting

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (events, alerts, users)
- **Graph Database**: Neo4j (attack paths, network topology)
- **Blockchain**: Web3.py (audit trail)
- **Authentication**: JWT with passlib
- **Async**: Motor (MongoDB async driver)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

The application requires the following environment variables (see `.env`):

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=cybergraph
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
BLOCKCHAIN_RPC_URL=http://localhost:8545
BLOCKCHAIN_CONTRACT_ADDRESS=0x...
AI_ENGINE_URL=http://localhost:8001
ATTACK_ENGINE_URL=http://localhost:8002
```

## Running the Application

Start the development server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
cyber-graph-backend/
├── app/
│   ├── api/
│   │   ├── controllers/    # Business logic controllers
│   │   └── routes/         # API route definitions
│   ├── config/             # Configuration settings
│   ├── integrations/       # External service clients
│   ├── middleware/         # Custom middleware
│   ├── models/            # Data models
│   ├── schemas/           # Pydantic schemas
│   ├── security/          # Security utilities
│   ├── services/          # Business services
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Events
- `GET /api/events/` - List events
- `POST /api/events/` - Create event
- `GET /api/events/{event_id}` - Get specific event

### Alerts
- `GET /api/alerts/` - List alerts
- `POST /api/alerts/` - Create alert

### Attack Paths
- `GET /api/attack-paths/` - List attack paths
- `POST /api/attack-paths/` - Create attack path

### Risk
- `GET /api/risk/` - List risks
- `POST /api/risk/` - Create risk assessment

### Statistics
- `GET /api/statistics/` - Get system statistics

### Health
- `GET /health/` - Health check
- `GET /health/services` - Service health status

## Development

The application is designed to be database-agnostic and will run even if MongoDB, Neo4j, or Blockchain services are not available. All database operations include proper error handling and will return appropriate error messages when services are unavailable.

## License

MIT License
