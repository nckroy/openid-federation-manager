# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

"""Unit tests for validation rules functionality."""

import pytest
import json


@pytest.mark.unit
class TestValidationRulesCRUD:
    """Tests for validation rule create, read, update, delete operations."""

    def test_create_validation_rule(self, federation_manager):
        """Test creating a validation rule."""
        success = federation_manager.create_validation_rule(
            rule_name='test_rule',
            entity_type='OP',
            field_path='metadata.openid_provider.issuer',
            validation_type='required',
            error_message='Issuer is required'
        )

        assert success is True

    def test_create_duplicate_rule_fails(self, federation_manager):
        """Test that creating duplicate rule name fails."""
        # Create first rule
        federation_manager.create_validation_rule(
            rule_name='test_rule',
            entity_type='OP',
            field_path='metadata.openid_provider.issuer',
            validation_type='required'
        )

        # Try to create duplicate
        success = federation_manager.create_validation_rule(
            rule_name='test_rule',
            entity_type='RP',
            field_path='metadata.openid_relying_party.client_id',
            validation_type='required'
        )

        assert success is False

    def test_get_validation_rules_empty(self, federation_manager):
        """Test getting rules when none exist."""
        rules = federation_manager.get_validation_rules()

        assert rules == []

    def test_get_validation_rules_all(self, federation_manager):
        """Test getting all validation rules."""
        # Create multiple rules
        federation_manager.create_validation_rule(
            'rule1', 'OP', 'metadata.openid_provider.issuer', 'required'
        )
        federation_manager.create_validation_rule(
            'rule2', 'RP', 'metadata.openid_relying_party.client_id', 'required'
        )
        federation_manager.create_validation_rule(
            'rule3', 'BOTH', 'jwks.keys', 'required'
        )

        rules = federation_manager.get_validation_rules(active_only=False)

        assert len(rules) == 3

    def test_get_validation_rules_filter_by_type(self, federation_manager):
        """Test filtering rules by entity type."""
        federation_manager.create_validation_rule(
            'rule1', 'OP', 'metadata.openid_provider.issuer', 'required'
        )
        federation_manager.create_validation_rule(
            'rule2', 'RP', 'metadata.openid_relying_party.client_id', 'required'
        )
        federation_manager.create_validation_rule(
            'rule3', 'BOTH', 'jwks.keys', 'required'
        )

        # Get OP rules (should include BOTH)
        op_rules = federation_manager.get_validation_rules(entity_type='OP')
        assert len(op_rules) == 2  # rule1 and rule3

        # Get RP rules (should include BOTH)
        rp_rules = federation_manager.get_validation_rules(entity_type='RP')
        assert len(rp_rules) == 2  # rule2 and rule3

    def test_get_validation_rules_active_only(self, federation_manager):
        """Test filtering for active rules only."""
        # Create active rule
        federation_manager.create_validation_rule(
            'active_rule', 'OP', 'metadata.openid_provider.issuer', 'required'
        )

        # Create inactive rule
        rule_id = federation_manager.create_validation_rule(
            'inactive_rule', 'OP', 'metadata.openid_provider.jwks_uri', 'required'
        )

        # Deactivate second rule
        conn = federation_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE validation_rules SET is_active = 0 WHERE rule_name = ?', ('inactive_rule',))
        conn.commit()
        conn.close()

        # Get active rules only
        active_rules = federation_manager.get_validation_rules(active_only=True)
        assert len(active_rules) == 1
        assert active_rules[0]['rule_name'] == 'active_rule'

        # Get all rules
        all_rules = federation_manager.get_validation_rules(active_only=False)
        assert len(all_rules) == 2

    def test_update_validation_rule(self, federation_manager):
        """Test updating a validation rule."""
        # Create rule
        federation_manager.create_validation_rule(
            'test_rule', 'OP', 'metadata.openid_provider.issuer', 'required'
        )

        # Get rule ID
        rules = federation_manager.get_validation_rules(active_only=False)
        rule_id = rules[0]['id']

        # Update rule
        success = federation_manager.update_validation_rule(
            rule_id,
            error_message='Updated error message',
            is_active=0
        )

        assert success is True

        # Verify update
        updated_rules = federation_manager.get_validation_rules(active_only=False)
        assert updated_rules[0]['error_message'] == 'Updated error message'
        assert updated_rules[0]['is_active'] == 0

    def test_delete_validation_rule(self, federation_manager):
        """Test deleting a validation rule."""
        # Create rule
        federation_manager.create_validation_rule(
            'test_rule', 'OP', 'metadata.openid_provider.issuer', 'required'
        )

        # Get rule ID
        rules = federation_manager.get_validation_rules(active_only=False)
        rule_id = rules[0]['id']

        # Delete rule
        success = federation_manager.delete_validation_rule(rule_id)

        assert success is True

        # Verify deletion
        remaining_rules = federation_manager.get_validation_rules(active_only=False)
        assert len(remaining_rules) == 0


@pytest.mark.unit
class TestValidationTypes:
    """Tests for different validation types."""

    def test_validation_required_field_present(self, federation_manager):
        """Test required validation passes when field exists."""
        federation_manager.create_validation_rule(
            'require_issuer',
            'OP',
            'metadata.openid_provider.issuer',
            'required',
            error_message='Issuer required'
        )

        metadata = {
            'openid_provider': {
                'issuer': 'https://op.example.com'
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is True
        assert len(errors) == 0

    def test_validation_required_field_missing(self, federation_manager):
        """Test required validation fails when field missing."""
        federation_manager.create_validation_rule(
            'require_issuer',
            'OP',
            'metadata.openid_provider.issuer',
            'required',
            error_message='Issuer required'
        )

        metadata = {
            'openid_provider': {}
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is False
        assert len(errors) == 1
        assert 'Issuer required' in errors[0]

    def test_validation_exact_value_match(self, federation_manager):
        """Test exact_value validation passes when values match."""
        federation_manager.create_validation_rule(
            'check_grant_type',
            'OP',
            'metadata.openid_provider.grant_types_supported',
            'exact_value',
            validation_value=json.dumps(['authorization_code']),
            error_message='Must support authorization_code'
        )

        metadata = {
            'openid_provider': {
                'grant_types_supported': ['authorization_code']
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is True
        assert len(errors) == 0

    def test_validation_exact_value_mismatch(self, federation_manager):
        """Test exact_value validation fails when values don't match."""
        federation_manager.create_validation_rule(
            'check_grant_type',
            'OP',
            'metadata.openid_provider.grant_types_supported',
            'exact_value',
            validation_value=json.dumps(['authorization_code']),
            error_message='Must support authorization_code'
        )

        metadata = {
            'openid_provider': {
                'grant_types_supported': ['implicit']
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is False
        assert len(errors) == 1

    def test_validation_regex_match(self, federation_manager):
        """Test regex validation passes when pattern matches."""
        federation_manager.create_validation_rule(
            'https_only',
            'OP',
            'metadata.openid_provider.issuer',
            'regex',
            validation_value='^https://.*',
            error_message='Must use HTTPS'
        )

        metadata = {
            'openid_provider': {
                'issuer': 'https://op.example.com'
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is True
        assert len(errors) == 0

    def test_validation_regex_no_match(self, federation_manager):
        """Test regex validation fails when pattern doesn't match."""
        federation_manager.create_validation_rule(
            'https_only',
            'OP',
            'metadata.openid_provider.issuer',
            'regex',
            validation_value='^https://.*',
            error_message='Must use HTTPS'
        )

        metadata = {
            'openid_provider': {
                'issuer': 'http://op.example.com'
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is False
        assert len(errors) == 1
        assert 'Must use HTTPS' in errors[0]

    def test_validation_range_within_bounds(self, federation_manager):
        """Test range validation passes when value is within range."""
        federation_manager.create_validation_rule(
            'token_lifetime',
            'OP',
            'metadata.openid_provider.default_max_age',
            'range',
            validation_value=json.dumps({'min': 60, 'max': 3600}),
            error_message='Lifetime must be 60-3600 seconds'
        )

        metadata = {
            'openid_provider': {
                'default_max_age': 1800
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is True
        assert len(errors) == 0

    def test_validation_range_below_minimum(self, federation_manager):
        """Test range validation fails when value below minimum."""
        federation_manager.create_validation_rule(
            'token_lifetime',
            'OP',
            'metadata.openid_provider.default_max_age',
            'range',
            validation_value=json.dumps({'min': 60, 'max': 3600}),
            error_message='Lifetime must be 60-3600 seconds'
        )

        metadata = {
            'openid_provider': {
                'default_max_age': 30
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is False
        assert len(errors) == 1

    def test_validation_range_above_maximum(self, federation_manager):
        """Test range validation fails when value above maximum."""
        federation_manager.create_validation_rule(
            'token_lifetime',
            'OP',
            'metadata.openid_provider.default_max_age',
            'range',
            validation_value=json.dumps({'min': 60, 'max': 3600}),
            error_message='Lifetime must be 60-3600 seconds'
        )

        metadata = {
            'openid_provider': {
                'default_max_age': 7200
            }
        }

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, {})

        assert is_valid is False
        assert len(errors) == 1

    def test_validation_multiple_rules(self, federation_manager):
        """Test multiple validation rules are all applied."""
        # Add multiple rules
        federation_manager.create_validation_rule(
            'require_issuer', 'OP', 'metadata.openid_provider.issuer', 'required'
        )
        federation_manager.create_validation_rule(
            'https_only', 'OP', 'metadata.openid_provider.issuer', 'regex', validation_value='^https://.*'
        )
        federation_manager.create_validation_rule(
            'require_jwks', 'OP', 'jwks.keys', 'required'
        )

        # Test with all rules passing
        metadata = {'openid_provider': {'issuer': 'https://op.example.com'}}
        jwks = {'keys': [{}]}

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is True
        assert len(errors) == 0

        # Test with some rules failing
        metadata = {'openid_provider': {'issuer': 'http://op.example.com'}}  # HTTP not HTTPS
        jwks = {}  # Missing keys

        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is False
        assert len(errors) >= 2  # At least regex and required failures
