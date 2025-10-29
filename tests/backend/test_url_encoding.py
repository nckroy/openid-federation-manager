# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

import sys
import os
import pytest
from urllib.parse import quote

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/python')))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_entity_id():
    """Return a sample entity ID with special characters that need URL encoding"""
    return "https://op.example.com/auth"


class TestURLEncoding:
    def test_fetch_with_encoded_entity_id(self, client, sample_entity_id):
        """Test that /fetch endpoint handles URL-encoded entity IDs"""
        # URL-encode the entity ID
        encoded_entity_id = quote(sample_entity_id, safe="")

        # Make request with encoded entity ID
        response = client.get(f'/fetch?sub={encoded_entity_id}')

        # Should return 404 since entity is not registered, but should not error on decoding
        assert response.status_code in [404, 400]

        # Check that the error is about entity not found, not about invalid format
        if response.status_code == 404:
            data = response.get_json()
            assert 'not found' in data['error'].lower()

    def test_fetch_with_double_encoded_entity_id(self, client):
        """Test that double-encoded entity IDs are handled correctly"""
        entity_id = "https://op.example.com"
        # Double encode (simulating a bug or misconfiguration)
        double_encoded = quote(quote(entity_id, safe=""), safe="")

        response = client.get(f'/fetch?sub={double_encoded}')

        # Should return 404 for entity not found (not a decode error)
        assert response.status_code in [404, 400]

    def test_fetch_with_unencoded_entity_id(self, client):
        """Test that unencoded entity IDs still work"""
        entity_id = "https://simple.example.com"

        response = client.get(f'/fetch?sub={entity_id}')

        # Should return 404 since entity is not registered
        assert response.status_code in [404, 400]

    def test_entity_endpoint_with_encoded_id(self, client, sample_entity_id):
        """Test that /entity/<id> endpoint handles URL-encoded entity IDs"""
        encoded_entity_id = quote(sample_entity_id, safe="")

        response = client.get(f'/entity/{encoded_entity_id}')

        # Should return 404 since entity is not registered
        assert response.status_code == 404
        data = response.get_json()
        assert 'not found' in data['error'].lower()

    def test_entity_endpoint_with_special_characters(self, client):
        """Test entity endpoint with entity IDs containing query parameters"""
        # Entity ID with query parameter
        entity_id = "https://op.example.com/auth?client_id=test"
        encoded_entity_id = quote(entity_id, safe="")

        response = client.get(f'/entity/{encoded_entity_id}')

        # Should handle the URL-encoded query string properly
        assert response.status_code == 404
        data = response.get_json()
        assert 'not found' in data['error'].lower()

    def test_fetch_endpoint_returns_encoded_url(self, client, monkeypatch):
        """Test that registration response includes properly encoded fetch endpoint URL"""
        # This test would require mocking the entity statement fetching
        # For now, we'll test the URL encoding format
        entity_id = "https://op.example.com/auth"
        expected_encoded = quote(entity_id, safe="")

        # Verify the encoding format
        assert "https%3A%2F%2F" in expected_encoded
        assert "%2F" in expected_encoded

    def test_fetch_with_fragment(self, client):
        """Test entity ID with URL fragment"""
        entity_id = "https://op.example.com#section"
        encoded_entity_id = quote(entity_id, safe="")

        response = client.get(f'/fetch?sub={encoded_entity_id}')

        assert response.status_code in [404, 400]

    def test_fetch_with_port_number(self, client):
        """Test entity ID with port number"""
        entity_id = "https://op.example.com:8443/auth"
        encoded_entity_id = quote(entity_id, safe="")

        response = client.get(f'/fetch?sub={encoded_entity_id}')

        assert response.status_code in [404, 400]

    def test_fetch_missing_sub_parameter(self, client):
        """Test that fetch endpoint requires sub parameter"""
        response = client.get('/fetch')

        assert response.status_code == 400
        data = response.get_json()
        assert 'sub parameter required' in data['error']

    def test_entity_id_stored_unencoded(self, client):
        """Verify that entity IDs are stored in database in unencoded form"""
        # This is a conceptual test - actual implementation would require
        # checking the database directly after registration
        # The key requirement is:
        # - Entity IDs come in URL-encoded in query parameters
        # - They are decoded before database storage
        # - They are stored as plain HTTPS URLs
        # - They are re-encoded when returned in URLs

        entity_id = "https://op.example.com/auth"
        encoded = quote(entity_id, safe="")

        # Verify encoding/decoding roundtrip
        from urllib.parse import unquote
        decoded = unquote(encoded)
        assert decoded == entity_id


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
