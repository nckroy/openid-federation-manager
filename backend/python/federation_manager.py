# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
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

    # Validation Rules Management

    def create_validation_rule(self, rule_name: str, entity_type: str,
                               field_path: str, validation_type: str,
                               validation_value: Optional[str] = None,
                               error_message: Optional[str] = None) -> bool:
        """Create a new validation rule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO validation_rules
                (rule_name, entity_type, field_path, validation_type, validation_value, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rule_name, entity_type, field_path, validation_type, validation_value, error_message))

            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_validation_rules(self, entity_type: Optional[str] = None,
                            active_only: bool = True) -> List[Dict]:
        """Get validation rules, optionally filtered by entity type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM validation_rules WHERE 1=1'
        params = []

        if active_only:
            query += ' AND is_active = 1'

        if entity_type:
            query += ' AND (entity_type = ? OR entity_type = "BOTH")'
            params.append(entity_type)

        cursor.execute(query, params)

        rules = []
        for row in cursor.fetchall():
            rules.append({
                'id': row['id'],
                'rule_name': row['rule_name'],
                'entity_type': row['entity_type'],
                'field_path': row['field_path'],
                'validation_type': row['validation_type'],
                'validation_value': row['validation_value'],
                'error_message': row['error_message'],
                'is_active': row['is_active'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })

        conn.close()
        return rules

    def update_validation_rule(self, rule_id: int, **kwargs) -> bool:
        """Update a validation rule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['rule_name', 'entity_type', 'field_path', 'validation_type',
                         'validation_value', 'error_message', 'is_active']

        updates = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f'{field} = ?')
                values.append(value)

        if not updates:
            conn.close()
            return False

        updates.append('updated_at = CURRENT_TIMESTAMP')
        values.append(rule_id)

        query = f'UPDATE validation_rules SET {", ".join(updates)} WHERE id = ?'

        try:
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
        except sqlite3.IntegrityError:
            success = False
        finally:
            conn.close()

        return success

    def delete_validation_rule(self, rule_id: int) -> bool:
        """Delete a validation rule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM validation_rules WHERE id = ?', (rule_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def _get_nested_value(self, data: Dict, path: str):
        """Get a nested value from a dictionary using dot notation"""
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return None
            else:
                return None

        return value

    def validate_entity_statement(self, entity_type: str, metadata: Dict, jwks: Dict) -> Tuple[bool, List[str]]:
        """
        Validate entity statement against configured rules
        Returns: (is_valid, error_messages)
        """
        rules = self.get_validation_rules(entity_type=entity_type, active_only=True)
        errors = []

        # Combine metadata and jwks for validation
        full_data = {
            'metadata': metadata,
            'jwks': jwks
        }

        for rule in rules:
            field_path = rule['field_path']
            validation_type = rule['validation_type']
            validation_value = rule['validation_value']
            error_message = rule['error_message'] or f"Validation failed for {field_path}"

            # Get the value from the entity statement
            actual_value = self._get_nested_value(full_data, field_path)

            # Apply validation based on type
            if validation_type == 'required':
                if actual_value is None:
                    errors.append(f"{error_message} (field is required)")

            elif validation_type == 'exists':
                if actual_value is None:
                    errors.append(f"{error_message} (field must exist)")

            elif validation_type == 'exact_value':
                if validation_value is None:
                    continue

                # Parse validation_value as JSON to support different types
                try:
                    expected_value = json.loads(validation_value)
                except (json.JSONDecodeError, TypeError):
                    expected_value = validation_value

                if actual_value != expected_value:
                    errors.append(f"{error_message} (expected: {expected_value}, got: {actual_value})")

            elif validation_type == 'regex':
                if validation_value is None:
                    continue

                if actual_value is None:
                    errors.append(f"{error_message} (field is missing)")
                    continue

                # Convert actual_value to string for regex matching
                actual_str = str(actual_value) if not isinstance(actual_value, str) else actual_value

                try:
                    if not re.match(validation_value, actual_str):
                        errors.append(f"{error_message} (does not match pattern: {validation_value})")
                except re.error as e:
                    errors.append(f"{error_message} (invalid regex pattern: {str(e)})")

            elif validation_type == 'range':
                if validation_value is None:
                    continue

                # Parse range as JSON: {"min": value, "max": value}
                try:
                    range_spec = json.loads(validation_value)
                    min_val = range_spec.get('min')
                    max_val = range_spec.get('max')

                    if actual_value is None:
                        errors.append(f"{error_message} (field is missing)")
                        continue

                    # Try to convert to number for comparison
                    try:
                        actual_num = float(actual_value) if not isinstance(actual_value, (int, float)) else actual_value

                        if min_val is not None and actual_num < min_val:
                            errors.append(f"{error_message} (value {actual_num} < minimum {min_val})")

                        if max_val is not None and actual_num > max_val:
                            errors.append(f"{error_message} (value {actual_num} > maximum {max_val})")

                    except (ValueError, TypeError):
                        errors.append(f"{error_message} (value is not numeric)")

                except (json.JSONDecodeError, TypeError):
                    errors.append(f"{error_message} (invalid range specification)")

        return (len(errors) == 0, errors)
