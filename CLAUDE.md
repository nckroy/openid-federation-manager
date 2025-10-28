# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenID Federation Manager is a lightweight application that implements OpenID Federation (draft 44) as an intermediate entity/federation operator. It manages registration and entity statements for OpenID Providers (OP) and Relying Parties (RP) in a federation.

## Architecture

### Backend Components

The Python/Flask backend implements the following architecture:

- **FederationManager** (`federation_manager.py`): Core federation logic handling entity registration, database operations, and cryptographic key management
- **EntityStatementManager** (`entity_statement.py`): Creates and verifies JWT-based entity statements, fetches statements from remote entities
- **Main Application** (`app.py`): HTTP API server exposing federation endpoints

### Database Layer

SQLite database (`database/schema.sql`) with four main tables:
- **entities**: Registered OPs and RPs with metadata and JWKS
- **entity_statements**: Signed JWT statements for subordinate entities
- **signing_keys**: RSA key pairs for signing statements
- **federation_config**: Configuration storage

### Federation Flow

1. **Entity Registration** (`POST /register`):
   - Fetches entity's `.well-known/openid-federation` statement
   - Validates entity type (OP or RP)
   - Stores metadata and JWKS
   - Creates subordinate statement signed by federation

2. **Statement Serving** (`GET /fetch?sub=<entity_id>`):
   - Returns signed subordinate statement for registered entities
   - Statements are cached and auto-renewed

3. **Federation Discovery** (`GET /.well-known/openid-federation`):
   - Returns federation's own entity statement with public keys

## Common Commands

### Setup and Run

```bash
# Install dependencies
cd backend/python
pip install -r requirements.txt

# Run server
python app.py
# Runs on port 5000 by default
```

## Configuration

Configuration is managed via `config/config.py`:

- **FEDERATION_ENTITY_ID**: Your federation's public URL (e.g., `https://federation.example.com`)
- **DATABASE_PATH**: SQLite database file location
- **API_HOST**: Server bind address
- **API_PORT**: Server listen port

Environment variables can be set in `.env` file (see `.env` for current values).

## Key Implementation Details

### Entity Statements (JWTs)

Entity statements are signed JWTs with header `typ: entity-statement+jwt` containing:
- Standard JWT claims: `iss`, `sub`, `iat`, `exp`
- `jwks`: Entity's JSON Web Key Set
- `metadata`: OpenID metadata (different structure for OPs, RPs, federation entities)
- `authority_hints`: Array of superior entities in federation hierarchy

### Cryptographic Operations

The implementation uses:
- RSA-2048 keys for signing (generated on first run)
- RS256 algorithm for JWT signatures
- `python-jose` library for cryptographic operations

Keys are persisted in the `signing_keys` table and automatically loaded on startup.

## API Endpoints

- `GET /.well-known/openid-federation` - Federation entity statement
- `POST /register` - Register new OP/RP (requires `entity_id` and `entity_type` in JSON body)
- `GET /fetch?sub=<entity_id>` - Get subordinate statement for entity
- `GET /list?entity_type=<OP|RP>` - List registered entities (optional filter)
- `GET /entity/<entity_id>` - Get entity details
- `GET /health` - Health check

## Development Notes

- Entity IDs must be full URLs (e.g., `https://op.example.com`)
- Statements have 24-hour validity (configurable via `STATEMENT_LIFETIME`)
- The federation automatically fetches and validates entity statements during registration
- Database schema is auto-created on first run
