# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

"""Shared pytest fixtures for all tests."""

import os
import sys
import tempfile
import pytest
import sqlite3

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.python.federation_manager import FederationManager
from backend.python.entity_statement import EntityStatementManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Initialize schema
    conn = sqlite3.connect(path)
    with open('database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

    yield path

    # Cleanup
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def federation_manager(temp_db):
    """Create a FederationManager instance with temporary database."""
    return FederationManager(temp_db)


@pytest.fixture
def entity_statement_manager(federation_manager):
    """Create an EntityStatementManager instance."""
    private_key, public_key = federation_manager.get_or_create_signing_key()
    return EntityStatementManager(
        federation_manager.get_connection(),
        'https://test-federation.example.com',
        private_key,
        public_key
    )


@pytest.fixture
def sample_op_metadata():
    """Sample OpenID Provider metadata."""
    return {
        "openid_provider": {
            "issuer": "https://op.example.com",
            "authorization_endpoint": "https://op.example.com/authorize",
            "token_endpoint": "https://op.example.com/token",
            "jwks_uri": "https://op.example.com/jwks",
            "scopes_supported": ["openid", "profile", "email"],
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "subject_types_supported": ["public"]
        }
    }


@pytest.fixture
def sample_rp_metadata():
    """Sample Relying Party metadata."""
    return {
        "openid_relying_party": {
            "client_id": "https://rp.example.com",
            "client_name": "Example RP",
            "redirect_uris": ["https://rp.example.com/callback"],
            "response_types": ["code"],
            "grant_types": ["authorization_code"]
        }
    }


@pytest.fixture
def sample_jwks():
    """Sample JWKS for testing."""
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key-1",
                "use": "sig",
                "n": "xGOr-H7A-PWlkK9FJW_MkJKmXXFrqKqZCG4RhITM8KH1qS_Z7L5Vz1rQ",
                "e": "AQAB"
            }
        ]
    }


@pytest.fixture
def flask_app():
    """Create a Flask app instance for testing."""
    import sys
    import os

    # Add backend to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'python'))

    from app import app
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask app."""
    return flask_app.test_client()
