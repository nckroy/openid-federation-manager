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

from backend.python.app import app
from config.config import Config


class TestAPI(unittest.TestCase):
    """Test cases for Flask API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the class"""
        # Create temporary directory for test database
        cls.test_dir = tempfile.mkdtemp()
        cls.test_db = os.path.join(cls.test_dir, 'test_api.db')

        # Override config
        Config.DATABASE_PATH = cls.test_db

        # Create test client
        app.config['TESTING'] = True
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        shutil.rmtree(cls.test_dir)

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_list_entities_empty(self):
        """Test listing entities when none exist"""
        response = self.client.get('/list')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('entities', data)
        self.assertEqual(len(data['entities']), 0)

    def test_register_entity_missing_params(self):
        """Test registration with missing parameters"""
        # Missing entity_type
        response = self.client.post('/register',
            json={'entity_id': 'https://test.example.com'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        # Missing entity_id
        response = self.client.post('/register',
            json={'entity_type': 'OP'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_entity_invalid_type(self):
        """Test registration with invalid entity type"""
        response = self.client.post('/register',
            json={
                'entity_id': 'https://test.example.com',
                'entity_type': 'INVALID'
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_fetch_nonexistent_entity(self):
        """Test fetching a non-existent entity"""
        response = self.client.get('/fetch?sub=https://nonexistent.example.com')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_nonexistent_entity(self):
        """Test getting details of non-existent entity"""
        response = self.client.get('/entity/https://nonexistent.example.com')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_fetch_missing_sub_parameter(self):
        """Test fetch endpoint without sub parameter"""
        response = self.client.get('/fetch')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_list_entities_with_filter(self):
        """Test listing entities with type filter"""
        # Test with OP filter
        response = self.client.get('/list?entity_type=OP')
        self.assertEqual(response.status_code, 200)

        # Test with RP filter
        response = self.client.get('/list?entity_type=RP')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
