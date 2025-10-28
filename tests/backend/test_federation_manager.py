# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

import unittest
import sys
import os
import json
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.python.federation_manager import FederationManager
from config.config import Config


class TestFederationManager(unittest.TestCase):
    """Test cases for FederationManager"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, 'test_federation.db')

        # Create test schema
        schema_path = os.path.join(os.path.dirname(__file__), '../../database/schema.sql')
        self.manager = FederationManager(self.test_db)

        # Read and execute schema
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            conn = self.manager.get_connection()
            conn.executescript(schema_sql)
            conn.close()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def test_generate_signing_key(self):
        """Test RSA key pair generation"""
        private_key, public_key = self.manager.generate_signing_key()

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertIn('BEGIN PRIVATE KEY', private_key)
        self.assertIn('BEGIN PUBLIC KEY', public_key)

    def test_store_and_retrieve_signing_key(self):
        """Test storing and retrieving signing keys"""
        private_key, public_key = self.manager.generate_signing_key()
        kid = 'test-key-1'

        # Store key
        self.manager.store_signing_key(kid, private_key, public_key)

        # Retrieve key
        retrieved = self.manager.get_signing_key(kid)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['kid'], kid)
        self.assertEqual(retrieved['private_key'], private_key)
        self.assertEqual(retrieved['public_key'], public_key)

    def test_register_entity(self):
        """Test entity registration"""
        entity_id = 'https://test-op.example.com'
        entity_type = 'OP'
        metadata = {'issuer': entity_id}
        jwks = {'keys': []}

        # Register entity
        result = self.manager.register_entity(
            entity_id,
            entity_type,
            metadata,
            jwks
        )

        self.assertTrue(result)

        # Verify entity exists
        entity = self.manager.get_entity(entity_id)
        self.assertIsNotNone(entity)
        self.assertEqual(entity['entity_id'], entity_id)
        self.assertEqual(entity['entity_type'], entity_type)

    def test_duplicate_entity_registration(self):
        """Test that duplicate registration fails"""
        entity_id = 'https://test-op.example.com'
        entity_type = 'OP'
        metadata = {'issuer': entity_id}
        jwks = {'keys': []}

        # First registration
        result1 = self.manager.register_entity(
            entity_id,
            entity_type,
            metadata,
            jwks
        )
        self.assertTrue(result1)

        # Second registration should fail
        result2 = self.manager.register_entity(
            entity_id,
            entity_type,
            metadata,
            jwks
        )
        self.assertFalse(result2)

    def test_list_entities(self):
        """Test listing entities"""
        # Register multiple entities
        entities_data = [
            ('https://op1.example.com', 'OP'),
            ('https://op2.example.com', 'OP'),
            ('https://rp1.example.com', 'RP'),
        ]

        for entity_id, entity_type in entities_data:
            self.manager.register_entity(
                entity_id,
                entity_type,
                {'issuer': entity_id},
                {'keys': []}
            )

        # List all entities
        all_entities = self.manager.list_entities()
        self.assertEqual(len(all_entities), 3)

        # List only OPs
        ops = self.manager.list_entities(entity_type='OP')
        self.assertEqual(len(ops), 2)

        # List only RPs
        rps = self.manager.list_entities(entity_type='RP')
        self.assertEqual(len(rps), 1)

    def test_store_entity_statement(self):
        """Test storing entity statements"""
        entity_id = 'https://test-op.example.com'
        issuer = 'https://federation.example.com'
        statement = 'test.jwt.token'
        expires_at = 1234567890

        # Store statement
        self.manager.store_entity_statement(
            entity_id,
            issuer,
            entity_id,
            statement,
            expires_at
        )

        # Retrieve statement
        retrieved = self.manager.get_entity_statement(entity_id)
        self.assertEqual(retrieved, statement)

    def test_get_jwks(self):
        """Test JWKS generation"""
        # Generate and store a key
        private_key, public_key = self.manager.generate_signing_key()
        kid = 'test-key-1'
        self.manager.store_signing_key(kid, private_key, public_key)

        # Get JWKS
        jwks = self.manager.get_jwks()

        self.assertIsNotNone(jwks)
        self.assertIn('keys', jwks)
        self.assertGreater(len(jwks['keys']), 0)


if __name__ == '__main__':
    unittest.main()
