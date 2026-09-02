# Cyber Graph - Ingestion API Documentation

## Overview

The Cyber Graph Ingestion API provides endpoints for ingesting, processing, and managing security events.

## Authentication

The API uses JWT (Bearer Token) authentication.

### Login

**POST** `/api/v1/auth/login`

```json
{
  "username": "admin",
  "password": "admin123"
}
```
