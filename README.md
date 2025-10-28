# OpenID Federation Manager

A lightweight Python application to manage an OpenID Federation (draft 44) as an intermediate entity/federation operator. This implementation allows you to operate as a federation authority that registers, manages, and issues subordinate statements for OpenID Providers (OP) and Relying Parties (RP).

## Features

- **Entity Registration**: Accept and register OpenID-enabled OP and RP entities
- **Automatic Entity Discovery**: Fetch entity statements from registered entities via `.well-known/openid-federation`
- **Subordinate Statement Generation**: Create and sign subordinate statements for registered entities
- **Cryptographic Key Management**: Automatic RSA-2048 key pair generation and management
- **SQLite Database**: Persistent storage for entities, statements, and signing keys
- **RESTful API**: Complete HTTP API for federation management

### Federation Endpoints

- `GET /.well-known/openid-federation` - Federation's own entity statement
- `POST /register` - Register new OP or RP entities
- `GET /fetch?sub=<entity_id>` - Fetch subordinate statements for entities
- `GET /list` - List all registered entities (optionally filter by type)
- `GET /entity/<entity_id>` - Get detailed information about a specific entity
- `GET /health` - Health check endpoint

## Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)

## Installation

You can set up the development environment using either Docker (recommended) or local installation.

### Option 1: Development Container (Recommended)

The easiest way to get started is using the Docker-based development container:

**Prerequisites:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

**Steps:**
1. Clone the repository:
   ```bash
   git clone https://github.com/nckroy/openid-federation-manager.git
   cd openid-federation-manager
   ```

2. Open in VS Code:
   ```bash
   code .
   ```

3. When prompted, click **"Reopen in Container"** (or press `F1` and select **"Dev Containers: Reopen in Container"**)

4. Wait for the container to build and dependencies to install automatically

5. The development environment is ready! See `.devcontainer/README.md` for more details.

### Option 2: Local Installation

If you prefer to install locally without Docker:

#### 1. Clone the Repository

```bash
git clone https://github.com/nckroy/openid-federation-manager.git
cd openid-federation-manager
```

#### 2. Install Dependencies

```bash
cd backend/python
pip install -r requirements.txt
```

#### 3. Configure Environment

Create a `.env` file in the project root or set environment variables:

```bash
# .env file
FEDERATION_ENTITY_ID=https://federation.example.com
API_HOST=0.0.0.0
API_PORT=5000
DATABASE_PATH=federation.db
ORGANIZATION_NAME=My Federation
```

**Configuration Options:**

- `FEDERATION_ENTITY_ID` - Your federation's public URL (required)
- `API_HOST` - Server bind address (default: `0.0.0.0`)
- `API_PORT` - Server listen port (default: `5000`)
- `DATABASE_PATH` - SQLite database file path (default: `federation.db`)
- `ORGANIZATION_NAME` - Your organization's name (default: `Example Federation`)

#### 4. Run the Application

From the project root directory:

```bash
python3 backend/python/app.py
```

The server will start on `http://0.0.0.0:5000` (or your configured host/port).

### Running in Development Container

If you're using the development container, simply open the integrated terminal in VS Code and run:

```bash
python3 backend/python/app.py
```

All dependencies are pre-installed, and ports 5000 and 5001 are automatically forwarded to your host machine.

## Usage

### Register an Entity

Register an OpenID Provider or Relying Party:

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "https://op.example.com",
    "entity_type": "OP"
  }'
```

**Parameters:**
- `entity_id` (string, required) - Full URL of the entity
- `entity_type` (string, required) - Either `"OP"` or `"RP"`

**Response:**
```json
{
  "status": "registered",
  "entity_id": "https://op.example.com",
  "fetch_endpoint": "https://federation.example.com/fetch?sub=https://op.example.com"
}
```

### Fetch Entity Statement

Retrieve a subordinate statement for a registered entity:

```bash
curl http://localhost:5000/fetch?sub=https://op.example.com
```

Returns a signed JWT (entity statement) with `Content-Type: application/entity-statement+jwt`

### List Registered Entities

List all registered entities:

```bash
curl http://localhost:5000/list
```

Filter by entity type:

```bash
curl http://localhost:5000/list?entity_type=OP
```

### Get Entity Details

Retrieve detailed information about a specific entity:

```bash
curl http://localhost:5000/entity/https://op.example.com
```

### Get Federation Entity Statement

Retrieve the federation's own entity statement:

```bash
curl http://localhost:5000/.well-known/openid-federation
```

## Architecture

### Components

- **FederationManager** (`federation_manager.py`) - Core federation logic, database operations, key management
- **EntityStatementManager** (`entity_statement.py`) - Entity statement creation, verification, and fetching
- **Flask Application** (`app.py`) - HTTP API server and route handlers

### Database Schema

The application uses SQLite with four main tables:

- **entities** - Registered OP and RP entities with metadata and JWKS
- **entity_statements** - Signed subordinate statements
- **signing_keys** - RSA key pairs for signing statements
- **federation_config** - Federation configuration storage

### Entity Statements

Entity statements are JWTs signed with RS256 containing:

- **Standard Claims**: `iss`, `sub`, `iat`, `exp`
- **jwks**: Entity's JSON Web Key Set
- **metadata**: OpenID metadata (varies by entity type)
- **authority_hints**: Array of superior entities in federation hierarchy
- **trust_marks**: Optional trust marks (future enhancement)

Statements have a 24-hour validity period (configurable via `STATEMENT_LIFETIME`). Statement expiration is checked using SQLite's `datetime('now')` comparison.

## Security Considerations

- RSA-2048 keys are automatically generated on first run
- Private keys are stored as PEM-encoded strings in the SQLite database
- The `.env` file and `*.db` files are excluded from version control
- Entity statements are cryptographically signed using RS256
- All entity IDs must be valid HTTPS URLs
- JWKS public keys use Base64url encoding without padding
- Keys are reused across application restarts for consistency

## Development

### Project Structure

```
openid-federation-manager/
├── backend/
│   └── python/
│       ├── app.py                    # Flask application
│       ├── federation_manager.py     # Core federation logic
│       ├── entity_statement.py       # Entity statement handling
│       └── requirements.txt          # Python dependencies
├── config/
│   └── config.py                     # Configuration management
├── database/
│   └── schema.sql                    # Database schema
├── CLAUDE.md                         # Development documentation
└── README.md                         # This file
```

### Running in Development Mode

The Flask application runs in debug mode by default when executed directly:

```bash
python3 backend/python/app.py
```

For production deployment, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## OpenID Federation Specification

This implementation follows the [OpenID Federation 1.0 - draft 44](https://openid.net/specs/openid-federation-1_0.html) specification.

### Key Concepts

- **Federation Entity**: An organization that operates the federation infrastructure
- **Entity Statement**: A signed JWT containing metadata and trust information about an entity
- **Subordinate Statement**: A statement issued by a superior entity (this federation) about a subordinate entity
- **Trust Chain**: A chain of entity statements establishing trust from a trust anchor

## Testing

The project includes comprehensive test suites for backend, frontend, and end-to-end integration testing.

### Running Backend Tests

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all backend tests (from project root)
python3 -m pytest tests/backend/ -v

# Run specific test file
python3 -m pytest tests/backend/test_federation_manager.py -v
python3 -m pytest tests/backend/test_api.py -v
```

**Note:** Backend tests must be run from the project root directory to correctly access `database/schema.sql`.

### Running Frontend Tests

```bash
# Install test dependencies
cd tests/frontend
npm install

# Run frontend tests
npm test
```

### Running Integration Tests

Integration tests verify the full stack (backend + frontend) works together:

```bash
# Manual method (start services first)
# Terminal 1: Start backend on port 5555
API_PORT=5555 python3 backend/python/app.py

# Terminal 2: Start frontend on port 3333
cd frontend
PORT=3333 API_URL=http://127.0.0.1:5555 npm start

# Terminal 3: Run integration tests
cd tests/integration
python3 test_full_stack.py
```

See `tests/README.md` for complete testing documentation.

## Troubleshooting

### Port Already in Use

If port 5000 is in use (common on macOS due to AirPlay):

```bash
# Option 1: Use a different port
API_PORT=5001 python3 backend/python/app.py

# Option 2: Disable AirPlay Receiver in System Preferences
```

### Database Already Exists

The application safely handles existing databases and will reuse existing signing keys. All schema operations use `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` for idempotency.

### Entity Statement Fetch Failures

Ensure the entity you're registering has a valid `.well-known/openid-federation` endpoint that returns a proper entity statement JWT.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

Copyright (c) 2025 Internet2

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) via [Happy](https://happy.engineering)
