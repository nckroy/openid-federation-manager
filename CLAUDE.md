# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenID Federation Manager is a Python/Flask application implementing OpenID Federation (draft 44) as an intermediate entity/federation operator. It manages registration and entity statements for OpenID Providers (OP) and Relying Parties (RP) in a federation.

**Copyright:** Copyright (c) 2025 Internet2
**License:** Apache License, Version 2.0

## Architecture

### Full-Stack Application

The application consists of two main components:

**Backend (Python/Flask):**
- **FederationManager** (`backend/python/federation_manager.py`): Core federation logic handling entity registration, database operations, and cryptographic key management
- **EntityStatementManager** (`backend/python/entity_statement.py`): Creates and verifies JWT-based entity statements, fetches statements from remote entities
- **Main Application** (`backend/python/app.py`): HTTP API server exposing federation endpoints
- **Configuration** (`config/config.py`): Centralized configuration management with environment variable support

**Frontend (Node.js/Express):**
- **Express Server** (`frontend/server.js`): Web UI server that proxies requests to the backend API
- **EJS Templates** (`frontend/views/`): Server-side rendered HTML pages
- **Static Assets** (`frontend/public/`): CSS and client-side JavaScript
- **Pages**: Dashboard, entity list, registration form, entity details, federation info

### Database Layer

SQLite database (`database/schema.sql`) with five main tables:
- **entities**: Registered OPs and RPs with metadata and JWKS
- **entity_statements**: Signed JWT statements for subordinate entities
- **signing_keys**: RSA key pairs for signing statements (auto-generated on first run)
- **federation_config**: Configuration storage
- **validation_rules**: Configurable validation rules for entity statement requirements

### Federation Flow

1. **Entity Registration** (`POST /register`):
   - Fetches entity's `.well-known/openid-federation` statement
   - Validates entity type (OP or RP)
   - **Applies validation rules** to ensure entity statement meets federation requirements
   - Stores metadata and JWKS in database
   - Creates subordinate statement signed by federation

2. **Statement Serving** (`GET /fetch?sub=<entity_id>`):
   - Returns signed subordinate statement for registered entities
   - Statements are cached in database and auto-renewed when expired

3. **Federation Discovery** (`GET /.well-known/openid-federation`):
   - Returns federation's own entity statement with public keys

## Common Commands

### Setup and Run

#### Using Development Container (Recommended)

The project includes a Docker Compose-based multi-service development environment:

1. Open project in VS Code
2. Press `F1` → "Dev Containers: Reopen in Container"
3. Wait for all containers to build and dependencies to install
4. Run the services:
   ```bash
   # Start backend (from app container terminal)
   python3 backend/python/app.py

   # Start frontend (in a separate terminal)
   cd frontend && npm start
   ```

**Multi-Service Architecture:**
- **Backend Container**: Python 3.11 with Flask API (ports 5000, 5001)
- **Frontend Container**: Node.js 18 with Express UI (port 3000)
- **App Container**: Main development workspace with both Python and Node.js tools
- All services connected via Docker network for inter-service communication
- Health checks ensure services start in correct order

**Features:**
- Python 3.11 and Node.js 18 pre-installed
- All dependencies auto-installed (Python + Node.js)
- Ports 3000, 5000, and 5001 auto-forwarded
- Persistent bash history
- Node modules cached for performance
- VS Code extensions (Pylance, Black, Flake8)

**Environment Variables:**
- Backend: `PYTHONPATH=/workspace`, `API_PORT=5000`
- Frontend: `API_URL=http://backend:5000`, `PORT=3000`
- Frontend connects to backend via Docker network using service name `backend`

See `.devcontainer/README.md` for detailed multi-service setup documentation.

#### Local Installation

**Backend:**
```bash
# Install Python dependencies
cd backend/python
pip3 install -r requirements.txt

# Run from project root
cd ../..
python3 backend/python/app.py

# Or with custom port
API_PORT=5001 python3 backend/python/app.py
```

**Frontend:**
```bash
# Install Node.js dependencies
cd frontend
npm install

# Run frontend (in separate terminal)
npm start

# Or with custom configuration
PORT=3001 API_URL=http://localhost:5001 npm start
```

**Important:**
- The backend must be run from the project root directory to correctly locate the `database/` and `config/` directories
- The frontend expects the backend to be running at `http://localhost:5000` by default (configurable via `API_URL`)
- Start backend first, then frontend

### Development

```bash
# Run backend with environment variables
FEDERATION_ENTITY_ID=https://my-federation.example.com \
API_PORT=5001 \
PYTHONPATH=/path/to/project \
python3 backend/python/app.py

# Run frontend with environment variables (in separate terminal)
PORT=3000 \
API_URL=http://localhost:5001 \
cd frontend && npm start
```

## Configuration

### Backend Configuration

Configuration is managed via `config/config.py` with environment variable overrides:

- **FEDERATION_ENTITY_ID**: Your federation's public URL (required, e.g., `https://federation.example.com`)
- **DATABASE_PATH**: SQLite database file location (default: `federation.db`)
- **API_HOST**: Server bind address (default: `0.0.0.0`)
- **API_PORT**: Server listen port (default: `5000`)
- **ORGANIZATION_NAME**: Federation organization name (default: `Example Federation`)
- **STATEMENT_LIFETIME**: Entity statement validity in seconds (default: `86400` = 24 hours)
- **PYTHONPATH**: Path to project root (required for module imports)

### Frontend Configuration

Frontend configuration via environment variables:

- **PORT**: Frontend server port (default: `3000`)
- **API_URL**: Backend API URL (default: `http://localhost:5000`)
- **NODE_ENV**: Environment mode (default: `development`)

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

#### Key API Signatures

**FederationManager methods:**
- `generate_signing_key()` → `(private_key, public_key, private_pem, public_pem)` - Returns 4 values: key objects and PEM strings
- `get_or_create_signing_key()` → `(private_key, public_key)` - Returns 2 values: key objects only
- `get_jwks()` → `Dict` - Returns JWKS with 'keys' array
- `register_entity(entity_id, entity_type, metadata, jwks)` → `bool` - Returns success status
- `get_entity(entity_id)` → `Optional[Dict]` - Returns entity dict or None
- `list_entities(entity_type=None)` → `List[str]` - Returns list of entity IDs
- `store_entity_statement(entity_id, issuer, subject, statement, expires_at)` → `None`
- `get_entity_statement(subject)` → `Optional[str]` - Returns JWT string or None if not found/expired
- `create_validation_rule(rule_name, entity_type, field_path, validation_type, validation_value, error_message)` → `bool`
- `get_validation_rules(entity_type=None, active_only=True)` → `List[Dict]`
- `update_validation_rule(rule_id, **kwargs)` → `bool`
- `delete_validation_rule(rule_id)` → `bool`
- `validate_entity_statement(entity_type, metadata, jwks)` → `Tuple[bool, List[str]]` - Returns validation result and error messages

## API Endpoints

### Backend API (Flask)

**Federation Endpoints:**
- `GET /.well-known/openid-federation` - Federation entity statement (JWT)
- `POST /register` - Register new OP/RP (requires `entity_id` and `entity_type` in JSON body)
- `GET /fetch?sub=<entity_id>` - Get subordinate statement for entity (JWT)
- `GET /list?entity_type=<OP|RP>` - List registered entities (optional filter)
- `GET /entity/<entity_id>` - Get entity details (JSON)
- `GET /health` - Health check (JSON)

**Validation Rules Endpoints:**
- `GET /validation-rules` - Get all validation rules (filter by `entity_type`, `active_only`)
- `POST /validation-rules` - Create new validation rule
- `PUT /validation-rules/<rule_id>` - Update validation rule
- `DELETE /validation-rules/<rule_id>` - Delete validation rule

All endpoints return appropriate HTTP status codes and JSON error messages on failure.

### Frontend UI (Express)

- `GET /` - Dashboard with entity statistics
- `GET /entities` - Entity list page with filtering
- `GET /register` - Entity registration form
- `POST /register` - Submit entity registration (proxies to backend)
- `GET /entity/:entityId` - Entity details page
- `GET /validation-rules` - Validation rules management page
- `POST /validation-rules` - Create new validation rule
- `POST /validation-rules/:id/delete` - Delete validation rule
- `POST /validation-rules/:id/toggle` - Enable/disable validation rule
- `GET /federation` - Federation information page
- `GET /health` - Frontend health check

The frontend server proxies API requests to the backend and renders HTML using EJS templates.

## Validation Rules Feature

The federation manager includes a configurable validation system that allows administrators to enforce specific requirements on entity statements during registration.

### Validation Types

1. **required** - Field must exist and have a non-null value
2. **exists** - Field must be present (can be null or empty)
3. **exact_value** - Field must match the specified value exactly (supports JSON for complex types)
4. **regex** - Field value must match the regular expression pattern
5. **range** - Numeric field must fall within the specified min/max range

### Field Path Syntax

Use dot notation to access nested fields:
- `metadata.openid_provider.issuer` - OP issuer URL
- `metadata.openid_provider.scopes_supported` - Supported scopes array
- `metadata.openid_relying_party.client_name` - RP client name
- `jwks.keys` - JWKS keys array

### Example Validation Rules

```python
# Require HTTPS for OP issuer
{
    "rule_name": "https_issuer",
    "entity_type": "OP",
    "field_path": "metadata.openid_provider.issuer",
    "validation_type": "regex",
    "validation_value": "^https://.*",
    "error_message": "Issuer must use HTTPS"
}

# Require specific grant types
{
    "rule_name": "authorization_code_required",
    "entity_type": "OP",
    "field_path": "metadata.openid_provider.grant_types_supported",
    "validation_type": "exact_value",
    "validation_value": '["authorization_code"]',
    "error_message": "Must support authorization_code grant type"
}

# Enforce token lifetime range
{
    "rule_name": "token_lifetime",
    "entity_type": "BOTH",
    "field_path": "metadata.openid_provider.default_max_age",
    "validation_type": "range",
    "validation_value": '{"min": 60, "max": 3600}',
    "error_message": "Token lifetime must be between 60 and 3600 seconds"
}
```

### Managing Validation Rules

**Via UI:**
1. Navigate to `/validation-rules` in the web interface
2. Use the form to add new rules with appropriate validation types
3. Enable/disable rules without deleting them
4. Delete rules when no longer needed

**Via API:**
```bash
# Create rule
curl -X POST http://localhost:5000/validation-rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "require_scopes",
    "entity_type": "OP",
    "field_path": "metadata.openid_provider.scopes_supported",
    "validation_type": "required",
    "error_message": "Scopes must be specified"
  }'

# List rules
curl http://localhost:5000/validation-rules

# Update rule
curl -X PUT http://localhost:5000/validation-rules/1 \
  -H "Content-Type: application/json" \
  -d '{"is_active": 0}'

# Delete rule
curl -X DELETE http://localhost:5000/validation-rules/1
```

### Validation Behavior

- Validation rules are applied automatically during entity registration (`POST /register`)
- If validation fails, registration is rejected with HTTP 400 and detailed error messages
- Only **active** rules are applied during validation
- Rules targeting `BOTH` entity types apply to both OPs and RPs
- Rules can be temporarily disabled without deletion by setting `is_active=0`

## Development Notes

### Important Constraints

- Entity IDs **must** be full HTTPS URLs (e.g., `https://op.example.com`)
- Statements have 24-hour validity by default (configurable via `STATEMENT_LIFETIME`)
- The federation automatically fetches and validates entity statements during registration
- **Validation rules are enforced during entity registration** - entities failing validation are rejected
- Database schema is auto-created on first run using `CREATE TABLE IF NOT EXISTS`
- The application runs in debug mode by default when executed directly
- Entity statements expire based on SQLite datetime comparison with `datetime('now')`
- Keys must be stored as PEM-formatted strings in the database
- JWKS format uses Base64url encoding without padding for 'n' and 'e' parameters

### File Organization

```
openid-federation-manager/
├── backend/
│   └── python/
│       ├── app.py                    # Flask API server
│       ├── federation_manager.py     # Core federation logic
│       ├── entity_statement.py       # Entity statement handling
│       └── requirements.txt          # Python dependencies
├── frontend/
│   ├── server.js                     # Express web server
│   ├── package.json                  # Node.js dependencies
│   ├── views/                        # EJS templates
│   │   ├── layout.ejs
│   │   ├── index.ejs
│   │   ├── entities.ejs
│   │   ├── register.ejs
│   │   ├── entity-details.ejs
│   │   └── federation.ejs
│   └── public/                       # Static assets
│       ├── css/style.css
│       └── js/main.js
├── config/
│   └── config.py                     # Configuration management
├── database/
│   └── schema.sql                    # Database schema
├── tests/
│   ├── backend/                      # Python backend tests
│   │   ├── test_federation_manager.py
│   │   └── test_api.py
│   ├── frontend/                     # Node.js frontend tests
│   │   ├── test_server.js
│   │   └── package.json
│   ├── integration/                  # End-to-end tests
│   │   ├── test_full_stack.py
│   │   └── docker-compose.test.yml
│   └── README.md                     # Testing documentation
├── .devcontainer/                    # Multi-service dev environment
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   ├── Dockerfile                    # Main dev container
│   ├── Dockerfile.backend            # Backend service
│   ├── Dockerfile.frontend           # Frontend service
│   └── README.md
├── CLAUDE.md                         # This file
└── README.md                         # Project documentation
```

**File Conventions:**
- All Python source files include Apache License 2.0 copyright headers
- All Node.js source files include Apache License 2.0 copyright headers
- Database file (`*.db`) is excluded from git
- Environment file (`.env`) is excluded from git
- `node_modules/` directories are excluded from git
- The project uses relative paths from project root

### Common Issues

1. **Port 5000 in use**: macOS AirPlay uses port 5000 by default. Use `API_PORT=5001` or disable AirPlay Receiver.
2. **Port 3000 in use**: If frontend port is occupied, use `PORT=3001 npm start` or kill conflicting process.
3. **Module not found errors**: Ensure you're running from the project root directory, not from `backend/python/`.
4. **Frontend can't connect to backend**: Check that backend is running and `API_URL` environment variable points to correct backend address.
5. **Database already exists error**: Fixed in current version - schema uses `IF NOT EXISTS` clauses.
6. **Tests must run from project root**: Backend tests expect to be run from project root to access `database/schema.sql`.
7. **Shared test database**: Tests may share database state; use isolation or cleanup between test runs if needed.
8. **Docker service communication**: In devcontainer, frontend uses `http://backend:5000` (Docker service name) not `http://localhost:5000`.

### Testing Endpoints

**Backend API:**
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

**Frontend UI:**
```bash
# Open in browser
open http://localhost:3000

# Or test with curl
curl http://localhost:3000/health
```

**Running Tests:**
```bash
# Backend tests (from project root)
python3 -m pytest tests/backend/ -v

# Frontend tests
cd tests/frontend && npm test

# Integration tests
cd tests/integration && python3 test_full_stack.py
```

## Code Style

**Python (Backend):**
- All code follows Apache License 2.0 header format
- Type hints used throughout (Python 3.8+)
- Docstrings on all public methods
- Error handling with try/except blocks
- Configuration via environment variables preferred over hardcoding
- Use Black formatter for code formatting
- Use Flake8 for linting

**JavaScript (Frontend):**
- All code follows Apache License 2.0 header format
- Use ES6+ syntax
- Async/await for asynchronous operations
- Error handling with try/catch blocks
- Configuration via environment variables
- Consistent indentation (2 spaces)

## Development Environment

### Using the Devcontainer

The project includes a complete Docker Compose-based multi-service development environment:

**Configuration Files:**
- `.devcontainer/devcontainer.json` - VS Code dev container configuration
- `.devcontainer/Dockerfile` - Main dev container image
- `.devcontainer/Dockerfile.backend` - Backend service container
- `.devcontainer/Dockerfile.frontend` - Frontend service container
- `.devcontainer/docker-compose.yml` - Multi-service orchestration
- `.devcontainer/README.md` - Detailed multi-service documentation

**What's Included:**
- **Backend Container**: Python 3.11 with Flask and all dependencies
- **Frontend Container**: Node.js 18 with Express and all dependencies
- **App Container**: Combined workspace with both Python and Node.js tools
- Git, SQLite3, and build tools
- VS Code extensions for Python and JavaScript development
- Pre-configured environment variables for all services
- Automatic port forwarding (3000, 5000, 5001)
- Persistent bash history
- Docker networking for inter-service communication
- Health checks for all services

**Architecture Benefits:**
- Services run in isolation but can communicate
- Frontend automatically connects to backend via Docker network
- Each service has optimized dependencies
- Node modules cached for better performance
- Services can be started/stopped independently

**When to Use:**
- Recommended for all new developers
- Ensures consistent full-stack environment across platforms
- No local Python/Node.js/dependency management needed
- Faster onboarding for full-stack development
- Testing inter-service communication

**When Not to Use:**
- If Docker Desktop is not available
- If you prefer managing Python/Node.js environments locally
- For production deployments (use local installation or separate production containers)

## Repository Information

- **GitHub**: https://github.com/nckroy/openid-federation-manager
- **License**: Apache License 2.0
- **Copyright**: Internet2 (2025)
