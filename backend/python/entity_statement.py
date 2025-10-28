# Copyright (c) 2025 Internet2
# Licensed under the MIT License - see LICENSE file for details

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import requests

class EntityStatementManager:
    def __init__(self, db_connection, federation_entity_id: str, private_key, public_key):
        self.db = db_connection
        self.federation_entity_id = federation_entity_id
        self.private_key = private_key
        self.public_key = public_key
    
    def fetch_entity_statement(self, entity_id: str) -> Optional[Dict]:
        """
        Fetch entity statement from the .well-known/openid-federation endpoint
        """
        well_known_url = f"{entity_id}/.well-known/openid-federation"
        
        try:
            response = requests.get(well_known_url, timeout=10)
            response.raise_for_status()
            
            # The response should be a JWT (entity statement)
            entity_statement_jwt = response.text
            
            # Decode without verification first to get the header
            unverified = jwt.decode(entity_statement_jwt, options={"verify_signature": False})
            
            return {
                'jwt': entity_statement_jwt,
                'payload': unverified
            }
        except Exception as e:
            print(f"Error fetching entity statement for {entity_id}: {str(e)}")
            return None
    
    def create_subordinate_statement(self, subject_entity_id: str, 
                                     metadata: Dict, 
                                     jwks: Dict,
                                     trust_marks: Optional[List[Dict]] = None) -> str:
        """
        Create a subordinate statement for a registered entity
        """
        now = int(time.time())
        exp = now + 86400  # 24 hours
        
        payload = {
            'iss': self.federation_entity_id,
            'sub': subject_entity_id,
            'iat': now,
            'exp': exp,
            'jwks': jwks,
            'metadata': metadata
        }
        
        if trust_marks:
            payload['trust_marks'] = trust_marks
        
        # Add authority hints pointing back to the federation
        payload['authority_hints'] = [self.federation_entity_id]
        
        # Sign the statement
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm='RS256',
            headers={'typ': 'entity-statement+jwt'}
        )
        
        return token
    
    def create_federation_entity_statement(self, jwks: Dict) -> str:
        """
        Create the federation's own entity statement
        """
        now = int(time.time())
        exp = now + 86400  # 24 hours
        
        payload = {
            'iss': self.federation_entity_id,
            'sub': self.federation_entity_id,
            'iat': now,
            'exp': exp,
            'jwks': jwks,
            'metadata': {
                'federation_entity': {
                    'organization_name': 'Example Federation',
                    'federation_fetch_endpoint': f'{self.federation_entity_id}/fetch',
                    'federation_list_endpoint': f'{self.federation_entity_id}/list',
                    'federation_resolve_endpoint': f'{self.federation_entity_id}/resolve',
                    'federation_trust_mark_status_endpoint': f'{self.federation_entity_id}/trust_mark_status'
                }
            }
        }
        
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm='RS256',
            headers={'typ': 'entity-statement+jwt'}
        )
        
        return token
    
    def verify_entity_statement(self, statement_jwt: str, expected_issuer: str) -> Optional[Dict]:
        """
        Verify an entity statement
        """
        try:
            # First decode to get the jwks
            unverified = jwt.decode(statement_jwt, options={"verify_signature": False})
            
            # Get the JWKS from the statement
            jwks = unverified.get('jwks', {})
            keys = jwks.get('keys', [])
            
            if not keys:
                return None
            
            # For simplicity, use the first key
            # In production, match by kid
            public_key_jwk = keys[0]
            
            # Convert JWK to public key object (simplified)
            # In production, use a proper JWK library
            verified_payload = jwt.decode(
                statement_jwt,
                self.public_key,  # This should be derived from JWK
                algorithms=['RS256'],
                options={'verify_exp': True}
            )
            
            if verified_payload.get('iss') != expected_issuer:
                return None
            
            return verified_payload
        except Exception as e:
            print(f"Error verifying entity statement: {str(e)}")
            return None
