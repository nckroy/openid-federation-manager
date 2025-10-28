# Development Container

This directory contains the configuration for a Docker-based development container for the OpenID Federation Manager project.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

## Getting Started

1. Open this project in VS Code
2. Press `F1` and select **"Dev Containers: Reopen in Container"**
3. Wait for the container to build and start
4. The Python dependencies will be automatically installed

## What's Included

- **Python 3.11** - Latest stable Python version
- **Git** - Version control
- **SQLite3** - Database CLI tools
- **VS Code Extensions**:
  - Python language support
  - Pylance (Python language server)
  - Black formatter
  - Flake8 linter
  - YAML support
  - GitHub Copilot (if you have access)

## Development Workflow

### Running the Application

From the integrated terminal in VS Code:

```bash
# Run the application (from workspace root)
python3 backend/python/app.py

# Or with custom configuration
API_PORT=5001 python3 backend/python/app.py
```

### Ports

The following ports are automatically forwarded:
- `5000` - Default application port
- `5001` - Alternative port

### Environment Variables

Default environment variables are set in `docker-compose.yml`:
- `FEDERATION_ENTITY_ID=https://federation.example.com`
- `API_HOST=0.0.0.0`
- `API_PORT=5000`
- `DATABASE_PATH=/workspace/federation.db`
- `ORGANIZATION_NAME=Example Federation`

You can override these in the terminal or by editing `docker-compose.yml`.

### Database

The SQLite database is stored at `/workspace/federation.db` which is mounted from your local workspace, so data persists between container rebuilds.

### Bash History

Your bash history is persisted in a Docker volume, so command history is preserved between sessions.

## Customization

### Adding Python Packages

Add packages to `backend/python/requirements.txt` and rebuild the container:
- Press `F1` → **"Dev Containers: Rebuild Container"**

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

### Container Won't Start

1. Check Docker Desktop is running
2. Check for port conflicts (5000, 5001)
3. Try rebuilding: `F1` → **"Dev Containers: Rebuild Container"**

### Python Packages Not Found

Run the install command manually:
```bash
pip3 install -r backend/python/requirements.txt
```

### Database Issues

Delete the database file and restart:
```bash
rm /workspace/federation.db
```

## License

Copyright (c) 2025 Internet2

Licensed under the Apache License, Version 2.0 - see LICENSE file for details.
