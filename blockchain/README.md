# Cyber Graph - Blockchain Audit & Integrity Verification Module

This module provides immutable audit logging, state hashing, and integrity-verification services for the **Cyber Graph** cybersecurity platform.

## Overview
- **Smart Contracts**: Solidity smart contracts deployed on Ethereum (Anvil for local development) for tamper-proof log storage and hash verification.
- **Python Service**: FastAPI service utilizing Web3.py to interact with smart contracts and perform cryptographic hashing (SHA-256).
- **Core Capabilities**:
  - Security event hashing and batching
  - Immutable audit trail recording on-chain
  - Cryptographic verification of historical records against on-chain hashes

## Project Structure
```
blockchain/
├── contracts/        # Solidity smart contracts
├── scripts/          # Deployment and maintenance scripts
├── app/              # Python application and Web3 integration
│   ├── config/       # Environment and application configuration
│   ├── core/         # Core business logic and blockchain client
│   ├── hashing/      # Event hashing and cryptographic utilities
│   ├── services/     # Blockchain interaction services
│   ├── schemas/      # Pydantic data schemas
│   ├── api/          # FastAPI API layer
│   │   └── routes/   # API route definitions
│   ├── storage/      # Local cache / storage handlers
│   └── utils/        # General helper utilities
├── abi/              # Compiled contract ABIs
├── deployments/      # Deployment logs and deployed addresses
├── tests/            # Test suites (pytest)
├── docs/             # Technical documentation and architecture diagrams
├── .env.example      # Example environment variables
├── .gitignore        # Git ignore rules
└── requirements.txt  # Python package dependencies
```

## Tech Stack
- **Language**: Python 3.10+, Solidity
- **Blockchain**: Anvil (Local EVM node), Hardhat
- **Web3 Interaction**: Web3.py
- **Testing**: pytest
- **Security Hashing**: SHA-256
