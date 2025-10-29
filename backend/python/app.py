# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

from flask import Flask, request, jsonify, Response
from urllib.parse import unquote, quote
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from federation_manager import FederationManager
from entity_statement import EntityStatementManager

app = Flask(__name__)
app.config.from_object(Config)

# Initialize managers
federation_manager = FederationManager(Config.DATABASE_PATH)
private_key, public_key = federation_manager.get_or_create_signing_key()

entity_statement_manager = EntityStatementManager(
    federation_manager.get_connection(),
    Config.FEDERATION_ENTITY_ID,
    private_key,
    public_key
)

@app.route('/.well-known/openid-federation', methods=['GET'])
def federation_entity_statement():
    """Return the federation's own entity statement"""
    jwks = federation_manager.get_jwks()
    statement = entity_statement_manager.create_federation_entity_statement(jwks)
    
    return Response(statement, mimetype='application/entity-statement+jwt')

@app.route('/register', methods=['POST'])
def register_entity():
    """Register a new OP or RP"""
    data = request.json
    
    entity_id = data.get('entity_id')
    entity_type = data.get('entity_type')  # 'OP' or 'RP'
    
    if not entity_id or not entity_type:
        return jsonify({'error': 'entity_id and entity_type required'}), 400
    
    if entity_type not in ['OP', 'RP']:
        return jsonify({'error': 'entity_type must be OP or RP'}), 400
    
    # Fetch entity statement from the entity
    entity_data = entity_statement_manager.fetch_entity_statement(entity_id)
    
    if not entity_data:
        return jsonify({'error': 'Could not fetch entity statement'}), 400
    
    payload = entity_data['payload']
    
    # Extract metadata and JWKS
    metadata = payload.get('metadata', {})
    jwks = payload.get('jwks', {})

    # Validate entity statement against configured rules
    is_valid, validation_errors = federation_manager.validate_entity_statement(
        entity_type, metadata, jwks
    )

    if not is_valid:
        return jsonify({
            'error': 'Entity statement validation failed',
            'validation_errors': validation_errors
        }), 400

    # Register the entity
    success = federation_manager.register_entity(
        entity_id,
        entity_type,
        metadata,
        jwks
    )

    if not success:
        return jsonify({'error': 'Entity already registered'}), 409
    
    # Create and store subordinate statement
    statement = entity_statement_manager.create_subordinate_statement(
        entity_id,
        metadata,
        jwks
    )
    
    # Decode to get expiration
    import jwt
    decoded = jwt.decode(statement, options={"verify_signature": False})
    
    federation_manager.store_entity_statement(
        entity_id,
        Config.FEDERATION_ENTITY_ID,
        entity_id,
        statement,
        decoded['exp']
    )
    
    return jsonify({
        'status': 'registered',
        'entity_id': entity_id,
        'fetch_endpoint': f'{Config.FEDERATION_ENTITY_ID}/fetch?sub={quote(entity_id, safe="")}'
    }), 201

@app.route('/fetch', methods=['GET'])
def fetch_entity():
    """Fetch endpoint - return subordinate statement for an entity"""
    subject = request.args.get('sub')

    if not subject:
        return jsonify({'error': 'sub parameter required'}), 400

    # Decode URL-encoded entity ID (e.g., https%3A%2F%2Fop.example.com -> https://op.example.com)
    subject = unquote(subject)

    # Check if entity is registered
    entity = federation_manager.get_entity(subject)
    
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
    
    # Get or create subordinate statement
    statement = federation_manager.get_entity_statement(subject)
    
    if not statement:
        # Create new statement
        statement = entity_statement_manager.create_subordinate_statement(
            subject,
            entity['metadata'],
            entity['jwks']
        )
        
        import jwt
        decoded = jwt.decode(statement, options={"verify_signature": False})
        
        federation_manager.store_entity_statement(
            subject,
            Config.FEDERATION_ENTITY_ID,
            subject,
            statement,
            decoded['exp']
        )
    
    return Response(statement, mimetype='application/entity-statement+jwt')

@app.route('/list', methods=['GET'])
def list_entities():
    """List all registered entities"""
    entity_type = request.args.get('entity_type')
    
    entities = federation_manager.list_entities(entity_type)
    
    return jsonify({'entities': entities})

@app.route('/entity/<path:entity_id>', methods=['GET'])
def get_entity_info(entity_id):
    """Get information about a specific entity"""
    # Decode URL-encoded entity ID
    entity_id = unquote(entity_id)

    # Ensure entity_id starts with http:// or https://
    if not entity_id.startswith('http'):
        entity_id = 'https://' + entity_id

    entity = federation_manager.get_entity(entity_id)
    
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
    
    return jsonify(entity)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

# Validation Rules Endpoints

@app.route('/validation-rules', methods=['GET'])
def get_validation_rules():
    """Get all validation rules"""
    entity_type = request.args.get('entity_type')
    active_only = request.args.get('active_only', 'true').lower() == 'true'

    rules = federation_manager.get_validation_rules(entity_type=entity_type, active_only=active_only)

    return jsonify({'rules': rules})

@app.route('/validation-rules', methods=['POST'])
def create_validation_rule():
    """Create a new validation rule"""
    data = request.json

    rule_name = data.get('rule_name')
    entity_type = data.get('entity_type')
    field_path = data.get('field_path')
    validation_type = data.get('validation_type')
    validation_value = data.get('validation_value')
    error_message = data.get('error_message')

    if not all([rule_name, entity_type, field_path, validation_type]):
        return jsonify({'error': 'rule_name, entity_type, field_path, and validation_type are required'}), 400

    if entity_type not in ['OP', 'RP', 'BOTH']:
        return jsonify({'error': 'entity_type must be OP, RP, or BOTH'}), 400

    if validation_type not in ['required', 'exact_value', 'regex', 'range', 'exists']:
        return jsonify({'error': 'Invalid validation_type'}), 400

    success = federation_manager.create_validation_rule(
        rule_name, entity_type, field_path, validation_type,
        validation_value, error_message
    )

    if not success:
        return jsonify({'error': 'Rule name already exists'}), 409

    return jsonify({'status': 'created', 'rule_name': rule_name}), 201

@app.route('/validation-rules/<int:rule_id>', methods=['PUT'])
def update_validation_rule(rule_id):
    """Update a validation rule"""
    data = request.json

    success = federation_manager.update_validation_rule(rule_id, **data)

    if not success:
        return jsonify({'error': 'Rule not found or invalid data'}), 404

    return jsonify({'status': 'updated', 'rule_id': rule_id})

@app.route('/validation-rules/<int:rule_id>', methods=['DELETE'])
def delete_validation_rule(rule_id):
    """Delete a validation rule"""
    success = federation_manager.delete_validation_rule(rule_id)

    if not success:
        return jsonify({'error': 'Rule not found'}), 404

    return jsonify({'status': 'deleted', 'rule_id': rule_id})

if __name__ == '__main__':
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=True
    )
