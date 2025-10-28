# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

import unittest
import sys
import os
import json
import time
import tempfile
import shutil
import subprocess
import requests
from multiprocessing import Process

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def start_backend():
    """Start the backend server"""
    os.chdir(os.path.join(os.path.dirname(__file__), '../..'))
    os.environ['API_PORT'] = '5555'
    os.environ['DATABASE_PATH'] = 'test_integration.db'
    from backend.python.app import app
    app.run(host='127.0.0.1', port=5555, debug=False)


def start_frontend():
    """Start the frontend server"""
    os.chdir(os.path.join(os.path.dirname(__file__), '../../frontend'))
    os.environ['PORT'] = '3333'
    os.environ['API_URL'] = 'http://127.0.0.1:5555'
    subprocess.run(['node', 'server.js'], check=False)


class TestFullStackIntegration(unittest.TestCase):
    """End-to-end integration tests"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.backend_url = 'http://127.0.0.1:5555'
        cls.frontend_url = 'http://127.0.0.1:3333'

        # Note: For full integration tests, backend and frontend
        # should be started manually before running tests
        # or use docker-compose for automated setup

        # Wait for services to be ready
        time.sleep(2)

    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f'{self.backend_url}/health', timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.ConnectionError:
            self.skipTest('Backend not running on port 5555')

    def test_frontend_health(self):
        """Test frontend health endpoint"""
        try:
            response = requests.get(f'{self.frontend_url}/health', timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('ui', data)
            self.assertIn('backend', data)
        except requests.exceptions.ConnectionError:
            self.skipTest('Frontend not running on port 3333')

    def test_backend_list_entities(self):
        """Test listing entities through backend"""
        try:
            response = requests.get(f'{self.backend_url}/list', timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('entities', data)
        except requests.exceptions.ConnectionError:
            self.skipTest('Backend not running')

    def test_frontend_dashboard(self):
        """Test frontend dashboard page"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Dashboard', response.text)
        except requests.exceptions.ConnectionError:
            self.skipTest('Frontend not running')

    def test_frontend_entities_page(self):
        """Test frontend entities page"""
        try:
            response = requests.get(f'{self.frontend_url}/entities', timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Registered Entities', response.text)
        except requests.exceptions.ConnectionError:
            self.skipTest('Frontend not running')

    def test_frontend_register_page(self):
        """Test frontend registration page"""
        try:
            response = requests.get(f'{self.frontend_url}/register', timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Register New Entity', response.text)
        except requests.exceptions.ConnectionError:
            self.skipTest('Frontend not running')

    def test_backend_invalid_registration(self):
        """Test invalid entity registration through backend"""
        try:
            response = requests.post(
                f'{self.backend_url}/register',
                json={
                    'entity_id': 'https://invalid.example.com',
                    'entity_type': 'INVALID'
                },
                timeout=5
            )
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn('error', data)
        except requests.exceptions.ConnectionError:
            self.skipTest('Backend not running')

    def test_backend_fetch_nonexistent(self):
        """Test fetching non-existent entity"""
        try:
            response = requests.get(
                f'{self.backend_url}/fetch?sub=https://nonexistent.example.com',
                timeout=5
            )
            self.assertEqual(response.status_code, 404)
        except requests.exceptions.ConnectionError:
            self.skipTest('Backend not running')


if __name__ == '__main__':
    # Check if services are running
    print("Note: Start backend on port 5555 and frontend on port 3333 before running tests")
    print("Backend: API_PORT=5555 python3 backend/python/app.py")
    print("Frontend: cd frontend && PORT=3333 API_URL=http://127.0.0.1:5555 npm start")
    print()

    unittest.main()
