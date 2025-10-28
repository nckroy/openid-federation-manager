# OpenID Federation Manager - Web UI

A Node.js-based web interface for the OpenID Federation Manager, providing an intuitive way to manage federation entities through a browser.

## Features

- **Dashboard** - Overview of registered entities with statistics
- **Entity Management** - Browse, filter, and view detailed information about registered entities
- **Entity Registration** - User-friendly form to register new OpenID Providers and Relying Parties
- **Federation Information** - View and decode the federation's entity statement
- **Responsive Design** - Works on desktop, tablet, and mobile devices

## Prerequisites

- Node.js 16+
- npm
- Running Python backend (see main README.md)

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment configuration:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` file with your settings:
   ```bash
   API_URL=http://localhost:5000      # Python backend URL
   PORT=3000                           # Frontend port
   FEDERATION_NAME=My Federation       # Display name
   ```

## Usage

### Development Mode

Run with auto-reload:
```bash
npm run dev
```

### Production Mode

```bash
npm start
```

The UI will be available at `http://localhost:3000` (or your configured port).

## Configuration

Environment variables (`.env` file):

- `API_URL` - Backend API URL (default: `http://localhost:5000`)
- `PORT` - Frontend server port (default: `3000`)
- `FEDERATION_NAME` - Federation display name (default: `OpenID Federation Manager`)

## Project Structure

```
frontend/
├── server.js              # Express application and routes
├── package.json           # Node.js dependencies
├── .env.example           # Environment configuration template
├── views/                 # EJS templates
│   ├── layout.ejs        # Main layout template
│   ├── index.ejs         # Dashboard page
│   ├── entities.ejs      # Entity list page
│   ├── register.ejs      # Registration form
│   ├── entity-details.ejs # Entity detail view
│   └── federation.ejs    # Federation information
└── public/               # Static assets
    ├── css/
    │   └── style.css     # Application styles
    └── js/
        └── main.js       # Client-side JavaScript
```

## API Proxy

The frontend acts as a proxy to the Python backend, providing these endpoints:

- `GET /` - Dashboard with entity statistics
- `GET /entities` - List all entities (filterable by type)
- `GET /register` - Registration form
- `POST /register` - Submit new entity registration
- `GET /entity/:entityId` - View entity details
- `GET /federation` - View federation statement
- `GET /health` - Health check (UI + backend)

## Development

### Adding New Pages

1. Create a new EJS template in `views/`
2. Add route handler in `server.js`
3. Add navigation link in `views/layout.ejs`

### Styling

Modify `public/css/style.css` for styling changes. The CSS uses CSS custom properties (variables) for easy theming.

### Client-Side JavaScript

Add interactive features in `public/js/main.js`.

## Production Deployment

For production, consider:

1. Using a process manager like PM2:
   ```bash
   npm install -g pm2
   pm2 start server.js --name federation-ui
   ```

2. Setting up a reverse proxy (nginx/Apache)

3. Using environment variables for configuration

4. Enabling HTTPS

## License

Copyright (c) 2025 Internet2

Licensed under the Apache License, Version 2.0 - see LICENSE file for details.
