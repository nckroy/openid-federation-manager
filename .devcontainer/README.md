# Development Container

This directory contains the configuration for a Docker-based development environment with multi-service support for the OpenID Federation Manager project. The development environment includes three separate containers that work together:

- **Backend** - Python/Flask API service
- **Frontend** - Node.js/Express web UI
- **App** - Main development container (for VS Code)

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

## Getting Started

1. Open this project in VS Code
2. Press `F1` and select **"Dev Containers: Reopen in Container"**
3. Wait for all containers to build and start (this may take a few minutes on first run)
4. The Python and Node.js dependencies will be automatically installed

## Architecture

The development environment consists of three Docker containers:

### Backend Container
- **Image**: Python 3.11 slim
- **Purpose**: Runs the Flask API server
- **Ports**: 5000, 5001
- **Health Check**: `/health` endpoint
- **Network**: Connected to `federation-network`

### Frontend Container
- **Image**: Node.js 18 slim
- **Purpose**: Runs the Express web UI
- **Port**: 3000
- **Health Check**: `/health` endpoint
- **Network**: Connected to `federation-network`
- **Dependencies**: Waits for backend to be healthy before starting

### App Container (Development)
- **Image**: Python 3.11 with development tools
- **Purpose**: Primary VS Code workspace
- **Network**: Connected to `federation-network`
- **Features**:
  - Python 3.11
  - Git
  - SQLite3
  - Persistent bash history

## What's Included

### Backend Service
- **Python 3.11** - Python runtime
- **Flask** - Web framework
- **SQLite3** - Database
- **Cryptography libraries** - JWT signing
- **Auto-installed dependencies** from `requirements.txt`

### Frontend Service
- **Node.js 18** - JavaScript runtime
- **Express** - Web framework
- **EJS** - Template engine
- **Auto-installed dependencies** from `package.json`

### VS Code Extensions
- Python language support
- Pylance (Python language server)
- Black formatter
- Flake8 linter
- YAML support
- GitHub Copilot (if you have access)

## Development Workflow

### Running the Services

The containers are always running but the services need to be started manually.

#### Start Backend Service

From the integrated terminal in VS Code:

```bash
# Connect to backend container and start service
docker-compose exec backend python3 backend/python/app.py
```

Or start it directly in the backend container:

```bash
# From the app container terminal
python3 backend/python/app.py
```

#### Start Frontend Service

From the integrated terminal in VS Code:

```bash
# Connect to frontend container and start service
docker-compose exec frontend npm start --prefix frontend
```

Or start it directly:

```bash
# From the app container terminal
cd frontend && npm start
```

### Accessing the Services

The following ports are automatically forwarded to your host:
- **`3000`** - Frontend web UI (http://localhost:3000)
- **`5000`** - Backend API (http://localhost:5000)
- **`5001`** - Alternative backend port

### Environment Variables

#### Backend Container
Environment variables set in `docker-compose.yml`:
- `FEDERATION_ENTITY_ID=https://federation.example.com`
- `API_HOST=0.0.0.0`
- `API_PORT=5000`
- `DATABASE_PATH=/workspace/federation.db`
- `ORGANIZATION_NAME=Example Federation`
- `PYTHONPATH=/workspace`

#### Frontend Container
Environment variables set in `docker-compose.yml`:
- `PORT=3000`
- `API_URL=http://backend:5000` (uses Docker network for service-to-service communication)
- `NODE_ENV=development`

You can override these in the terminal or by editing `docker-compose.yml`.

### Inter-Service Communication

The backend and frontend containers communicate via Docker networking:
- Frontend connects to backend using `http://backend:5000`
- Your browser connects to frontend using `http://localhost:3000`
- Your browser connects to backend using `http://localhost:5000`

### Database

The SQLite database is stored at `/workspace/federation.db` which is mounted from your local workspace, so data persists between container rebuilds.

### Bash History

Your bash history is persisted in a Docker volume, so command history is preserved between sessions.

### Node Modules Caching

Frontend `node_modules` are cached in a separate Docker volume for better performance.

## Customization

### Adding Python Packages

1. Add packages to `backend/python/requirements.txt`
2. Rebuild the containers: Press `F1` → **"Dev Containers: Rebuild Container"**

### Adding Node.js Packages

1. Add packages to `frontend/package.json`
2. Rebuild the containers: Press `F1` → **"Dev Containers: Rebuild Container"**

Or install manually in the frontend container:
```bash
docker-compose exec frontend npm install <package-name>
```

### Adding VS Code Extensions

Edit `devcontainer.json` and add extension IDs to the `extensions` array, then rebuild.

### Changing Python Version

Edit the `features` section in `devcontainer.json`:

```json
"features": {
    "ghcr.io/devcontainers/features/python:1": {
        "version": "3.12"  // Change version here
    }
}
```

## Troubleshooting

### Containers Won't Start

1. Check Docker Desktop is running
2. Check for port conflicts (3000, 5000, 5001)
3. Check Docker logs: `docker-compose logs`
4. Try rebuilding: `F1` → **"Dev Containers: Rebuild Container"**

### Backend Health Check Failing

The frontend depends on the backend health check passing. If the backend is unhealthy:

1. Check backend logs: `docker-compose logs backend`
2. Verify the backend is listening on port 5000
3. Test health endpoint: `curl http://localhost:5000/health`

### Frontend Can't Connect to Backend

If you see connection errors in the frontend:

1. Verify backend is running: `docker-compose ps`
2. Check backend is healthy: `docker-compose exec backend curl http://localhost:5000/health`
3. Verify network connectivity: `docker-compose exec frontend ping backend`

### Python Packages Not Found

Run the install command manually in the app or backend container:
```bash
pip3 install -r backend/python/requirements.txt
```

### Node Modules Not Found

Run the install command manually in the frontend container:
```bash
docker-compose exec frontend npm install
```

### Database Issues

Delete the database file and restart:
```bash
rm /workspace/federation.db
```

### Viewing Container Logs

View logs from all containers:
```bash
docker-compose logs -f
```

View logs from specific container:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f app
```

## License

Copyright (c) 2025 Internet2

Licensed under the Apache License, Version 2.0 - see LICENSE file for details.
