# OpenID Federation Manager - Testing

This directory contains comprehensive tests for the OpenID Federation Manager, including unit tests, API tests, and end-to-end integration tests.

## Test Structure

```
tests/
├── backend/               # Python backend tests
│   ├── test_federation_manager.py
│   └── test_api.py
├── frontend/              # Node.js frontend tests
│   ├── test_server.js
│   └── package.json
├── integration/           # End-to-end integration tests
│   ├── test_full_stack.py
│   └── docker-compose.test.yml
└── README.md             # This file
```

## Prerequisites

### Backend Tests
- Python 3.8+
- pytest (install: `pip install pytest`)

### Frontend Tests
- Node.js 16+
- npm

### Integration Tests
- Both backend and frontend running
- Docker and docker-compose (for automated testing)

## Running Tests

### Backend Unit Tests

**Important:** All backend tests must be run from the project root directory.

Test the FederationManager class:

```bash
python3 -m pytest tests/backend/test_federation_manager.py -v
```

Test the Flask API:

```bash
python3 -m pytest tests/backend/test_api.py -v
```

Run all backend tests:

```bash
python3 -m pytest tests/backend/ -v
```

### Frontend Tests

Install dependencies:

```bash
cd tests/frontend
npm install
```

Run frontend tests:

```bash
cd tests/frontend
npm test
```

### Integration Tests

#### Manual Method

1. Start the backend on port 5555:
   ```bash
   API_PORT=5555 python3 backend/python/app.py
   ```

2. Start the frontend on port 3333 (in another terminal):
   ```bash
   cd frontend
   PORT=3333 API_URL=http://127.0.0.1:5555 npm start
   ```

3. Run integration tests (in another terminal):
   ```bash
   cd tests/integration
   python3 test_full_stack.py
   ```

#### Docker Method (Recommended)

Use docker-compose to run all services and tests automatically:

```bash
cd tests/integration
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## Test Coverage

### Backend Tests (`test_federation_manager.py`)

- ✅ RSA key pair generation (4-value return: private_key, public_key, private_pem, public_pem)
- ✅ Signing key storage and retrieval (PEM format in database)
- ✅ Entity registration
- ✅ Duplicate entity detection
- ✅ Entity listing and filtering (by entity_type)
- ✅ Entity statement storage with expiry
- ✅ JWKS generation (Base64url encoding without padding)

### API Tests (`test_api.py`)

- ✅ Health check endpoint
- ✅ List entities (empty and with filters)
- ✅ Register entity (validation and errors)
- ✅ Fetch entity statements
- ✅ Get entity details
- ✅ Error handling (404, 400 responses)

### Frontend Tests (`test_server.js`)

- ✅ Dashboard page rendering
- ✅ Entity list page with filtering
- ✅ Registration form display
- ✅ Entity registration submission
- ✅ Entity details page
- ✅ Federation information page
- ✅ Health check endpoint
- ✅ Error handling and graceful degradation

### Integration Tests (`test_full_stack.py`)

- ✅ Backend health check
- ✅ Frontend health check
- ✅ Backend API endpoints
- ✅ Frontend page rendering
- ✅ Error handling across stack
- ✅ Service communication

## Writing New Tests

### Backend Test Example

```python
import unittest
from backend.python.federation_manager import FederationManager

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.manager = FederationManager('test.db')

    def test_new_functionality(self):
        result = self.manager.new_method()
        self.assertTrue(result)
```

### Frontend Test Example

```javascript
describe('New Feature', function() {
    it('should do something', function(done) {
        chai.request(app)
            .get('/new-endpoint')
            .end(function(err, res) {
                expect(res).to.have.status(200);
                done();
            });
    });
});
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/python/requirements.txt
          pip install pytest
      - name: Run backend tests
        run: |
          cd tests/backend
          python -m pytest . -v
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      - name: Install frontend dependencies
        run: |
          cd tests/frontend
          npm install
      - name: Run frontend tests
        run: |
          cd tests/frontend
          npm test
```

## Troubleshooting

### Backend Tests Failing

- **Must run from project root**: Tests expect `database/schema.sql` to be accessible
- Verify all Python dependencies are installed: `pip install -r tests/requirements.txt`
- Check that temporary directories can be created (tests use `tempfile.mkdtemp()`)

### Frontend Tests Failing

- Run `npm install` in `tests/frontend` directory
- Check that the frontend server code is correct
- Ensure mock API responses match expected format

### Integration Tests Failing

- Verify both backend and frontend are running
- Check port availability (5555 for backend, 3333 for frontend)
- Ensure services are accessible (firewall, network issues)
- Wait for services to fully start before running tests

## License

Copyright (c) 2025 Internet2

Licensed under the Apache License, Version 2.0 - see LICENSE file for details.
