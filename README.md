# OpenID Federation Manager

A lightweight Python application to manage an OpenID Federation (draft 44) as an intermediate entity/federation operator. This implementation allows you to operate as a federation authority that registers, manages, and issues subordinate statements for OpenID Providers (OP) and Relying Parties (RP).

## Features

- **Entity Registration**: Accept and register OpenID-enabled OP and RP entities
- **Automatic Entity Discovery**: Fetch entity statements from registered entities via `.well-known/openid-federation`
- **Validation Rules**: Configurable requirements for entity statements with regex, exact value, and range validation
- **Subordinate Statement Generation**: Create and sign subordinate statements for registered entities
- **Cryptographic Key Management**: Automatic RSA-2048 key pair generation and management
- **SQLite Database**: Persistent storage for entities, statements, and signing keys
- **RESTful API**: Complete HTTP API for federation management
- **Web UI**: User-friendly interface for managing entities and validation rules

### Federation Endpoints

- `GET /.well-known/openid-federation` - Federation's own entity statement
- `POST /register` - Register new OP or RP entities
- `GET /fetch?sub=<entity_id>` - Fetch subordinate statements for entities
- `GET /list` - List all registered entities (optionally filter by type)
- `GET /entity/<entity_id>` - Get detailed information about a specific entity
- `GET /health` - Health check endpoint

## Prerequisites

### Backend
- **Python 3.8+**
- **pip** (Python package manager)

### Frontend
- **Node.js 18+**
- **npm** (Node package manager)

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

If you're using the development container, the backend and frontend services are pre-configured. Simply open the integrated terminal in VS Code and run:

**Backend:**
```bash
python3 backend/python/app.py
```

**Frontend (in a separate terminal):**
```bash
cd frontend && npm start
```

All dependencies are pre-installed, and ports 3000, 5000, and 5001 are automatically forwarded to your host machine.

## Running the Frontend

The OpenID Federation Manager includes a web-based user interface built with Node.js and Express. The frontend provides a dashboard, entity management, registration forms, and federation information displays.

### Frontend Architecture

- **Express Server** (`frontend/server.js`) - Web UI server that proxies API requests to the backend
- **EJS Templates** (`frontend/views/`) - Server-side rendered HTML pages
- **Static Assets** (`frontend/public/`) - CSS and client-side JavaScript
- **Pages**: Dashboard, entity list, registration form, entity details, federation info

### Option 1: Running Frontend in Development Container

**Prerequisites:**
- Development container already set up (see "Option 1: Development Container" above)
- Backend service running on port 5000

**Steps:**

1. Open a terminal in VS Code (inside the dev container)

2. Start the backend service (if not already running):
   ```bash
   python3 backend/python/app.py
   ```

3. In a **separate terminal**, start the frontend:
   ```bash
   cd frontend
   npm start
   ```

4. Access the web UI at http://localhost:3000

**Environment Variables (Dev Container):**
These are pre-configured in `.devcontainer/docker-compose.yml`:
- `PORT=3000` - Frontend server port
- `API_URL=http://backend:5000` - Backend API endpoint (uses Docker network)
- `NODE_ENV=development` - Development mode

### Option 2: Running Frontend Locally

**Prerequisites:**
- Node.js 18+ and npm installed
- Backend service running (see "Option 2: Local Installation" above)

**Steps:**

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (first time only):
   ```bash
   npm install
   ```

3. Configure environment variables (optional):
   ```bash
   # Create .env file in frontend directory
   PORT=3000
   API_URL=http://localhost:5000
   NODE_ENV=development
   ```

4. Start the frontend server:
   ```bash
   npm start
   ```

5. Access the web UI at http://localhost:3000

**Configuration Options:**

You can override default settings using environment variables:

```bash
# Run on custom port with custom backend URL
PORT=3001 API_URL=http://localhost:5001 npm start
```

- `PORT` - Frontend server port (default: `3000`)
- `API_URL` - Backend API URL (default: `http://localhost:5000`)
- `NODE_ENV` - Environment mode (default: `development`)

### Option 3: Running Frontend with Docker Compose

**Prerequisites:**
- Docker and Docker Compose installed
- Backend service container running

**Steps:**

1. Start all services using Docker Compose:
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml up
   ```

   Or start services individually:
   ```bash
   # Start backend
   docker-compose -f .devcontainer/docker-compose.yml up backend

   # Start frontend (in separate terminal)
   docker-compose -f .devcontainer/docker-compose.yml up frontend
   ```

2. Access the web UI at http://localhost:3000

**Docker Compose Features:**
- **Multi-service architecture** - Backend, frontend, and app containers
- **Automatic dependency management** - Frontend waits for backend health check
- **Inter-service networking** - Containers communicate via `federation-network`
- **Health checks** - Ensures services start in correct order
- **Volume mounting** - Source code mounted for live development
- **Node modules caching** - Faster rebuilds and better performance

**View logs:**
```bash
# All services
docker-compose -f .devcontainer/docker-compose.yml logs -f

# Specific service
docker-compose -f .devcontainer/docker-compose.yml logs -f frontend
docker-compose -f .devcontainer/docker-compose.yml logs -f backend
```

**Stop services:**
```bash
docker-compose -f .devcontainer/docker-compose.yml down
```

### Frontend Features

The web interface provides:

1. **Dashboard** (`/`) - Overview of registered entities and federation statistics
2. **Entity List** (`/entities`) - Browse and filter registered OPs and RPs
3. **Registration** (`/register`) - Register new entities with the federation
4. **Entity Details** (`/entity/:entityId`) - View detailed entity information, metadata, and JWKS
5. **Federation Info** (`/federation`) - View federation entity statement and configuration

### Testing the Frontend

**Access the UI:**
```bash
# Default URL
open http://localhost:3000

# Or with curl
curl http://localhost:3000/health
```

**Frontend API Endpoints:**
- `GET /` - Dashboard page
- `GET /entities` - Entity list page with filtering
- `GET /register` - Entity registration form
- `POST /register` - Submit entity registration (proxies to backend)
- `GET /entity/:entityId` - Entity details page
- `GET /federation` - Federation information page
- `GET /health` - Frontend health check

### Troubleshooting Frontend

**Port 3000 Already in Use:**
```bash
# Option 1: Use a different port
PORT=3001 npm start

# Option 2: Kill the process using port 3000
lsof -ti:3000 | xargs kill
```

**Frontend Can't Connect to Backend:**
1. Verify backend is running:
   ```bash
   curl http://localhost:5000/health
   ```

2. Check `API_URL` environment variable:
   ```bash
   echo $API_URL
   ```

3. For Docker environments, use service name instead of localhost:
   ```bash
   # In docker-compose environments
   API_URL=http://backend:5000
   ```

**Dependencies Not Installing:**
```bash
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Docker Network Issues:**

If frontend can't reach backend in Docker:
```bash
# Verify network connectivity
docker-compose -f .devcontainer/docker-compose.yml exec frontend ping backend

# Check backend is healthy
docker-compose -f .devcontainer/docker-compose.yml exec backend curl http://localhost:5000/health
```

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

For entity IDs with special characters (paths, query parameters, etc.), URL-encode the entity ID:

```bash
# Entity ID with path: https://op.example.com/auth
curl "http://localhost:5000/fetch?sub=https%3A%2F%2Fop.example.com%2Fauth"

# Or let curl handle encoding with --data-urlencode
curl -G http://localhost:5000/fetch --data-urlencode "sub=https://op.example.com/auth"
```

Returns a signed JWT (entity statement) with `Content-Type: application/entity-statement+jwt`

**Note:** The frontend automatically URL-encodes entity IDs when making requests.

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

For entity IDs with special characters, URL-encode the entity ID:

```bash
# Entity ID with path: https://op.example.com/auth
curl "http://localhost:5000/entity/https%3A%2F%2Fop.example.com%2Fauth"
```

### Get Federation Entity Statement

Retrieve the federation's own entity statement:

```bash
curl http://localhost:5000/.well-known/openid-federation
```

### URL Encoding for Entity IDs

Entity IDs are full HTTPS URLs that may contain special characters requiring URL encoding when used in HTTP requests.

**Automatic Handling:**
- **Frontend**: Automatically URL-encodes entity IDs using `encodeURIComponent()` when making API calls
- **Backend**: Automatically URL-decodes entity IDs from query parameters and path segments using `unquote()`
- **Database**: Stores entity IDs in their original, unencoded form (e.g., `https://op.example.com/auth`)

**When URL Encoding is Required:**
Entity IDs containing any of these characters need encoding:
- Paths: `https://op.example.com/auth`
- Query parameters: `https://op.example.com?client_id=test`
- Port numbers: `https://op.example.com:8443`
- Fragments: `https://op.example.com#section`

**Examples:**
```bash
# Entity ID without special characters (encoding optional)
https://op.example.com

# Entity ID with path (must be encoded)
https://op.example.com/auth  →  https%3A%2F%2Fop.example.com%2Fauth

# Entity ID with query parameter (must be encoded)
https://op.example.com?id=123  →  https%3A%2F%2Fop.example.com%3Fid%3D123
```

**Using curl with URL encoding:**
```bash
# Option 1: Manual encoding
curl "http://localhost:5000/fetch?sub=https%3A%2F%2Fop.example.com%2Fauth"

# Option 2: Let curl encode (recommended)
curl -G http://localhost:5000/fetch --data-urlencode "sub=https://op.example.com/auth"
```

## Architecture

### Components

- **FederationManager** (`federation_manager.py`) - Core federation logic, database operations, key management
- **EntityStatementManager** (`entity_statement.py`) - Entity statement creation, verification, and fetching
- **Flask Application** (`app.py`) - HTTP API server and route handlers

### Database Schema

The application uses SQLite with five main tables:

- **entities** - Registered OP and RP entities with metadata and JWKS
- **entity_statements** - Signed subordinate statements
- **signing_keys** - RSA key pairs for signing statements
- **federation_config** - Federation configuration storage
- **validation_rules** - Configurable validation rules for entity statement requirements

### Entity Statements

Entity statements are JWTs signed with RS256 containing:

- **Standard Claims**: `iss`, `sub`, `iat`, `exp`
- **jwks**: Entity's JSON Web Key Set
- **metadata**: OpenID metadata (varies by entity type)
- **authority_hints**: Array of superior entities in federation hierarchy
- **trust_marks**: Optional trust marks (future enhancement)

Statements have a 24-hour validity period (configurable via `STATEMENT_LIFETIME`). Statement expiration is checked using SQLite's `datetime('now')` comparison.

## Validation Rules

The federation manager includes a powerful validation system that allows administrators to enforce specific requirements on entity statements during registration.

### Validation Types

1. **required** - Field must exist and have a non-null value
2. **exists** - Field must be present (can be null or empty)
3. **exact_value** - Field must match the specified value exactly (supports JSON for complex types)
4. **regex** - Field value must match the regular expression pattern
5. **range** - Numeric field must fall within the specified min/max range

### Managing Validation Rules

**Via Web UI:**
Navigate to the **Validation Rules** page in the web interface to:
- Create new validation rules with a user-friendly form
- Enable/disable rules without deleting them
- View all configured rules in a searchable table
- Delete rules that are no longer needed

**Via API:**
```bash
# Create a rule requiring HTTPS for OP issuers
curl -X POST http://localhost:5000/validation-rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "https_issuer",
    "entity_type": "OP",
    "field_path": "metadata.openid_provider.issuer",
    "validation_type": "regex",
    "validation_value": "^https://.*",
    "error_message": "Issuer must use HTTPS"
  }'

# List all validation rules
curl http://localhost:5000/validation-rules

# Update a rule (e.g., disable it)
curl -X PUT http://localhost:5000/validation-rules/1 \
  -H "Content-Type: application/json" \
  -d '{"is_active": 0}'

# Delete a rule
curl -X DELETE http://localhost:5000/validation-rules/1
```

### Example Use Cases

- **Enforce HTTPS**: Require all OP issuer URLs to use HTTPS protocol
- **Mandate grant types**: Ensure OPs support specific OAuth grant types
- **Token lifetime limits**: Enforce minimum and maximum token lifetimes
- **Required scopes**: Mandate specific OAuth scopes be supported
- **Client naming conventions**: Require RP client names to follow naming patterns

Validation rules are automatically applied during entity registration. If an entity fails validation, registration is rejected with detailed error messages explaining what requirements were not met.

## Security Considerations

- RSA-2048 keys are automatically generated on first run
- Private keys are stored as PEM-encoded strings in the SQLite database
- The `.env` file and `*.db` files are excluded from version control
- Entity statements are cryptographically signed using RS256
- All entity IDs must be valid HTTPS URLs
- JWKS public keys use Base64url encoding without padding
- Keys are reused across application restarts for consistency
- Validation rules enforce federation security policies during entity registration

## Development

### Project Structure

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
│   │   ├── layout.ejs                # Base template with navigation
│   │   ├── index.ejs                 # Dashboard page
│   │   ├── entities.ejs              # Entity list page
│   │   ├── register.ejs              # Entity registration form
│   │   ├── entity-details.ejs        # Entity details page
│   │   ├── federation.ejs            # Federation info page
│   │   └── validation-rules.ejs      # Validation rules management
│   └── public/                       # Static assets
│       ├── css/style.css             # Application styles
│       └── js/main.js                # Client-side JavaScript
├── config/
│   └── config.py                     # Configuration management
├── database/
│   └── schema.sql                    # Database schema (5 tables)
├── tests/
│   ├── backend/                      # Python backend tests
│   │   ├── test_federation_manager.py
│   │   ├── test_validation_rules.py  # Validation rules tests
│   │   └── test_api.py
│   ├── frontend/                     # Node.js frontend tests
│   │   ├── test_server.js
│   │   └── package.json
│   ├── integration/                  # End-to-end tests
│   │   ├── test_full_stack.py
│   │   └── docker-compose.test.yml
│   └── README.md                     # Testing documentation
├── .devcontainer/                    # Multi-service dev environment
│   ├── devcontainer.json             # VS Code dev container config
│   ├── docker-compose.yml            # Multi-service orchestration
│   ├── Dockerfile                    # Main dev container
│   ├── Dockerfile.backend            # Backend service container
│   ├── Dockerfile.frontend           # Frontend service container
│   └── README.md                     # Dev container documentation
├── .github/
│   └── pull_request_template.md      # PR template for contributions
├── CLAUDE.md                         # Development documentation
├── CONTRIBUTING.md                   # Contributor guidelines
├── LICENSE                           # Apache License 2.0
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

Contributions are welcome! This project uses a feature branch workflow with pull requests for all changes.

**Quick Start:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following the coding standards
4. Write/update tests
5. Submit a pull request

**Documentation:**
- See [CONTRIBUTING.md](CONTRIBUTING.md) for complete contributor guidelines
- See [CLAUDE.md](CLAUDE.md) for development workflow and technical details
- Use the [pull request template](.github/pull_request_template.md) when submitting PRs

**Branch Naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

**Requirements:**
- Follow project coding standards (Python: PEP 8, Black, Flake8; JavaScript: ES6+)
- Add tests for new functionality
- Update documentation as needed
- All tests must pass before PR approval

Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting your first contribution.

## License

Copyright (c) 2025 Internet2

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) via [Happy](https://happy.engineering)
