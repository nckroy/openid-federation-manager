# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import jwt

class FederationManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize the database with schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Read and execute schema
        with open('database/schema.sql', 'r') as f:
            cursor.executescript(f.read())
        
        conn.commit()
        conn.close()
    
    def generate_signing_key(self) -> tuple:
        """Generate a new RSA key pair for signing"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_key, public_key, private_pem, public_pem
    
    def get_or_create_signing_key(self) -> tuple:
        """Get active signing key or create new one"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT private_key, public_key 
            FROM signing_keys 
            WHERE is_active = 1 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        
        if row:
            private_pem = row['private_key']
            public_pem = row['public_key']
            
            private_key = serialization.load_pem_private_key(
                private_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            
            public_key = serialization.load_pem_public_key(
                public_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            conn.close()
            return private_key, public_key
        
        # Generate new key
        private_key, public_key, private_pem, public_pem = self.generate_signing_key()
        
        # Generate kid
        import hashlib
        kid = hashlib.sha256(public_pem.encode()).hexdigest()[:16]
        
        cursor.execute('''
            INSERT INTO signing_keys (kid, key_type, private_key, public_key, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (kid, 'RSA', private_pem, public_pem))
        
        conn.commit()
        conn.close()
        
        return private_key, public_key
    
    def get_jwks(self) -> Dict:
        """Get public JWKS for the federation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT kid, public_key 
            FROM signing_keys 
            WHERE is_active = 1
        ''')
        
        keys = []
        for row in cursor.fetchall():
            public_key = serialization.load_pem_public_key(
                row['public_key'].encode('utf-8'),
                backend=default_backend()
            )
            
            # Convert to JWK format
            public_numbers = public_key.public_numbers()
            
            import base64
            def int_to_base64(n):
                byte_length = (n.bit_length() + 7) // 8
                return base64.urlsafe_b64encode(
                    n.to_bytes(byte_length, byteorder='big')
                ).rstrip(b'=').decode('utf-8')
            
            jwk = {
                'kty': 'RSA',
                'kid': row['kid'],
                'use': 'sig',
                'n': int_to_base64(public_numbers.n),
                'e': int_to_base64(public_numbers.e)
            }
            
            keys.append(jwk)
        
        conn.close()
        
        return {'keys': keys}
    
    def register_entity(self, entity_id: str, entity_type: str, 
                       metadata: Dict, jwks: Dict) -> bool:
        """Register a new entity (OP or RP)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO entities (entity_id, entity_type, metadata, jwks, status)
                VALUES (?, ?, ?, ?, 'active')
            ''', (
                entity_id,
                entity_type,
                json.dumps(metadata),
                json.dumps(jwks)
            ))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get entity information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM entities WHERE entity_id = ? AND status = 'active'
        ''', (entity_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'entity_id': row['entity_id'],
                'entity_type': row['entity_type'],
                'metadata': json.loads(row['metadata']),
                'jwks': json.loads(row['jwks']),
                'status': row['status'],
                'registered_at': row['registered_at']
            }
        
        return None
    
    def list_entities(self, entity_type: Optional[str] = None) -> List[str]:
        """List all registered entities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if entity_type:
            cursor.execute('''
                SELECT entity_id FROM entities 
                WHERE entity_type = ? AND status = 'active'
            ''', (entity_type,))
        else:
            cursor.execute('''
                SELECT entity_id FROM entities WHERE status = 'active'
            ''')
        
        entities = [row['entity_id'] for row in cursor.fetchall()]
        conn.close()
        
        return entities
    
    def store_entity_statement(self, entity_id: str, issuer: str, 
                               subject: str, statement: str, expires_at: int):
        """Store a signed entity statement"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO entity_statements 
            (entity_id, issuer, subject, statement, expires_at)
            VALUES (?, ?, ?, ?, datetime(?, 'unixepoch'))
        ''', (entity_id, issuer, subject, statement, expires_at))
        
        conn.commit()
        conn.close()
    
    def get_entity_statement(self, subject: str) -> Optional[str]:
        """Get the latest entity statement for a subject"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT statement FROM entity_statements
            WHERE subject = ? AND expires_at > datetime('now')
            ORDER BY issued_at DESC
            LIMIT 1
        ''', (subject,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row['statement'] if row else None
