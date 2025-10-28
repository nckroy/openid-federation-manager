# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenID Federation Manager is a Python/Flask application implementing OpenID Federation (draft 44) as an intermediate entity/federation operator. It manages registration and entity statements for OpenID Providers (OP) and Relying Parties (RP) in a federation.

**Copyright:** Copyright (c) 2025 Internet2
**License:** Apache License, Version 2.0

## Architecture

### Backend Components

The Python/Flask backend implements the following architecture:

- **FederationManager** (`backend/python/federation_manager.py`): Core federation logic handling entity registration, database operations, and cryptographic key management
- **EntityStatementManager** (`backend/python/entity_statement.py`): Creates and verifies JWT-based entity statements, fetches statements from remote entities
- **Main Application** (`backend/python/app.py`): HTTP API server exposing federation endpoints
- **Configuration** (`config/config.py`): Centralized configuration management with environment variable support

### Database Layer

SQLite database (`database/schema.sql`) with four main tables:
- **entities**: Registered OPs and RPs with metadata and JWKS
- **entity_statements**: Signed JWT statements for subordinate entities
- **signing_keys**: RSA key pairs for signing statements (auto-generated on first run)
- **federation_config**: Configuration storage

### Federation Flow

1. **Entity Registration** (`POST /register`):
   - Fetches entity's `.well-known/openid-federation` statement
   - Validates entity type (OP or RP)
   - Stores metadata and JWKS in database
   - Creates subordinate statement signed by federation

2. **Statement Serving** (`GET /fetch?sub=<entity_id>`):
   - Returns signed subordinate statement for registered entities
   - Statements are cached in database and auto-renewed when expired

3. **Federation Discovery** (`GET /.well-known/openid-federation`):
   - Returns federation's own entity statement with public keys

## Common Commands

### Setup and Run

```bash
# Install dependencies
cd backend/python
pip3 install -r requirements.txt

# Run from project root
cd ../..
python3 backend/python/app.py

# Or with custom port
API_PORT=5001 python3 backend/python/app.py
```

**Important:** The application must be run from the project root directory to correctly locate the `database/` and `config/` directories.

### Development

```bash
# Run with environment variables
FEDERATION_ENTITY_ID=https://my-federation.example.com \
API_PORT=5001 \
python3 backend/python/app.py
```

## Configuration

Configuration is managed via `config/config.py` with environment variable overrides:

- **FEDERATION_ENTITY_ID**: Your federation's public URL (required, e.g., `https://federation.example.com`)
- **DATABASE_PATH**: SQLite database file location (default: `federation.db`)
- **API_HOST**: Server bind address (default: `0.0.0.0`)
- **API_PORT**: Server listen port (default: `5000`)
- **ORGANIZATION_NAME**: Federation organization name (default: `Example Federation`)
- **STATEMENT_LIFETIME**: Entity statement validity in seconds (default: `86400` = 24 hours)

Environment variables can be set in `.env` file in project root (excluded from git).

## Key Implementation Details

### Entity Statements (JWTs)

Entity statements are signed JWTs with header `typ: entity-statement+jwt` containing:
- **Standard JWT claims**: `iss`, `sub`, `iat`, `exp`
- **jwks**: Entity's JSON Web Key Set
- **metadata**: OpenID metadata (structure varies by entity type)
- **authority_hints**: Array of superior entities in federation hierarchy
- **trust_marks**: Optional trust marks (planned feature)

### Cryptographic Operations

The implementation uses:
- **RSA-2048 keys** for signing (auto-generated on first run)
- **RS256 algorithm** for JWT signatures
- **PyJWT library** for JWT operations
- **cryptography library** for RSA key generation and management

Keys are persisted in the `signing_keys` table and automatically loaded on startup. The application reuses existing keys across restarts.

## API Endpoints

- `GET /.well-known/openid-federation` - Federation entity statement (JWT)
- `POST /register` - Register new OP/RP (requires `entity_id` and `entity_type` in JSON body)
- `GET /fetch?sub=<entity_id>` - Get subordinate statement for entity (JWT)
- `GET /list?entity_type=<OP|RP>` - List registered entities (optional filter)
- `GET /entity/<entity_id>` - Get entity details (JSON)
- `GET /health` - Health check (JSON)

All endpoints return appropriate HTTP status codes and JSON error messages on failure.

## Development Notes

### Important Constraints

- Entity IDs **must** be full HTTPS URLs (e.g., `https://op.example.com`)
- Statements have 24-hour validity by default (configurable via `STATEMENT_LIFETIME`)
- The federation automatically fetches and validates entity statements during registration
- Database schema is auto-created on first run using `CREATE TABLE IF NOT EXISTS`
- The application runs in debug mode by default when executed directly

### File Organization

- All Python source files include Apache License 2.0 copyright headers
- Database file (`*.db`) is excluded from git
- Environment file (`.env`) is excluded from git
- The project uses relative paths from project root

### Common Issues

1. **Port 5000 in use**: macOS AirPlay uses port 5000 by default. Use `API_PORT=5001` or disable AirPlay Receiver.
2. **Module not found errors**: Ensure you're running from the project root directory, not from `backend/python/`.
3. **Database already exists error**: Fixed in current version - schema uses `IF NOT EXISTS` clauses.

### Testing Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Get federation statement
curl http://localhost:5000/.well-known/openid-federation

# Register an entity (requires valid entity with openid-federation endpoint)
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "https://op.example.com", "entity_type": "OP"}'

# List entities
curl http://localhost:5000/list
```

## Code Style

- All code follows Apache License 2.0 header format
- Type hints used throughout (Python 3.8+)
- Docstrings on all public methods
- Error handling with try/except blocks
- Configuration via environment variables preferred over hardcoding

## Repository Information

- **GitHub**: https://github.com/nckroy/openid-federation-manager
- **License**: Apache License 2.0
- **Copyright**: Internet2 (2025)
