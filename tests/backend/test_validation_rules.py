# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details

import sys
import os
import pytest
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/python')))

from federation_manager import FederationManager


@pytest.fixture
def federation_manager(tmp_path):
    """Create a FederationManager instance with a temporary database"""
    db_path = tmp_path / "test_validation.db"
    return FederationManager(str(db_path))


class TestValidationRules:
    def test_create_validation_rule(self, federation_manager):
        """Test creating a validation rule"""
        success = federation_manager.create_validation_rule(
            rule_name="test_rule",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="required",
            error_message="Issuer is required"
        )

        assert success is True

        # Verify rule was created
        rules = federation_manager.get_validation_rules()
        assert len(rules) == 1
        assert rules[0]['rule_name'] == 'test_rule'
        assert rules[0]['entity_type'] == 'OP'

    def test_duplicate_rule_name(self, federation_manager):
        """Test that duplicate rule names are rejected"""
        federation_manager.create_validation_rule(
            rule_name="test_rule",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="required"
        )

        # Try to create another rule with the same name
        success = federation_manager.create_validation_rule(
            rule_name="test_rule",
            entity_type="RP",
            field_path="metadata.openid_relying_party.client_name",
            validation_type="required"
        )

        assert success is False

    def test_get_validation_rules_by_entity_type(self, federation_manager):
        """Test filtering rules by entity type"""
        federation_manager.create_validation_rule(
            rule_name="op_rule",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="required"
        )

        federation_manager.create_validation_rule(
            rule_name="rp_rule",
            entity_type="RP",
            field_path="metadata.openid_relying_party.client_name",
            validation_type="required"
        )

        federation_manager.create_validation_rule(
            rule_name="both_rule",
            entity_type="BOTH",
            field_path="jwks.keys",
            validation_type="required"
        )

        # Get OP rules (should include OP and BOTH)
        op_rules = federation_manager.get_validation_rules(entity_type="OP")
        assert len(op_rules) == 2
        rule_names = [r['rule_name'] for r in op_rules]
        assert 'op_rule' in rule_names
        assert 'both_rule' in rule_names

        # Get RP rules (should include RP and BOTH)
        rp_rules = federation_manager.get_validation_rules(entity_type="RP")
        assert len(rp_rules) == 2
        rule_names = [r['rule_name'] for r in rp_rules]
        assert 'rp_rule' in rule_names
        assert 'both_rule' in rule_names

    def test_update_validation_rule(self, federation_manager):
        """Test updating a validation rule"""
        federation_manager.create_validation_rule(
            rule_name="test_rule",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="required"
        )

        rules = federation_manager.get_validation_rules()
        rule_id = rules[0]['id']

        # Update the rule
        success = federation_manager.update_validation_rule(
            rule_id,
            validation_type="regex",
            validation_value="^https://.*"
        )

        assert success is True

        # Verify update
        rules = federation_manager.get_validation_rules()
        assert rules[0]['validation_type'] == 'regex'
        assert rules[0]['validation_value'] == '^https://.*'

    def test_delete_validation_rule(self, federation_manager):
        """Test deleting a validation rule"""
        federation_manager.create_validation_rule(
            rule_name="test_rule",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="required"
        )

        rules = federation_manager.get_validation_rules()
        rule_id = rules[0]['id']

        # Delete the rule
        success = federation_manager.delete_validation_rule(rule_id)
        assert success is True

        # Verify deletion
        rules = federation_manager.get_validation_rules()
        assert len(rules) == 0

    def test_validate_required_field(self, federation_manager):
        """Test validation of required fields"""
        federation_manager.create_validation_rule(
            rule_name="require_issuer",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="required",
            error_message="Issuer is required"
        )

        # Test with missing field
        metadata = {'openid_provider': {}}
        jwks = {'keys': []}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is False
        assert len(errors) == 1
        assert 'Issuer is required' in errors[0]

        # Test with present field
        metadata = {'openid_provider': {'issuer': 'https://op.example.com'}}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_exact_value(self, federation_manager):
        """Test validation of exact value"""
        federation_manager.create_validation_rule(
            rule_name="require_grant_type",
            entity_type="OP",
            field_path="metadata.openid_provider.grant_types_supported",
            validation_type="exact_value",
            validation_value='["authorization_code"]',
            error_message="Must support authorization_code"
        )

        # Test with wrong value
        metadata = {'openid_provider': {'grant_types_supported': ['implicit']}}
        jwks = {'keys': []}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is False
        assert len(errors) == 1

        # Test with correct value
        metadata = {'openid_provider': {'grant_types_supported': ['authorization_code']}}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_regex(self, federation_manager):
        """Test validation with regex pattern"""
        federation_manager.create_validation_rule(
            rule_name="https_issuer",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="regex",
            validation_value="^https://.*",
            error_message="Issuer must use HTTPS"
        )

        # Test with invalid pattern
        metadata = {'openid_provider': {'issuer': 'http://op.example.com'}}
        jwks = {'keys': []}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is False
        assert 'HTTPS' in errors[0]

        # Test with valid pattern
        metadata = {'openid_provider': {'issuer': 'https://op.example.com'}}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is True

    def test_validate_range(self, federation_manager):
        """Test validation with numeric range"""
        federation_manager.create_validation_rule(
            rule_name="token_lifetime",
            entity_type="OP",
            field_path="metadata.openid_provider.default_max_age",
            validation_type="range",
            validation_value='{"min": 60, "max": 3600}',
            error_message="Token lifetime must be between 60 and 3600 seconds"
        )

        # Test with value below minimum
        metadata = {'openid_provider': {'default_max_age': 30}}
        jwks = {'keys': []}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is False

        # Test with value above maximum
        metadata = {'openid_provider': {'default_max_age': 7200}}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is False

        # Test with value in range
        metadata = {'openid_provider': {'default_max_age': 1800}}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is True

    def test_inactive_rules_not_applied(self, federation_manager):
        """Test that inactive rules are not applied during validation"""
        federation_manager.create_validation_rule(
            rule_name="test_rule",
            entity_type="OP",
            field_path="metadata.openid_provider.issuer",
            validation_type="required"
        )

        # Get the rule and deactivate it
        rules = federation_manager.get_validation_rules()
        rule_id = rules[0]['id']
        federation_manager.update_validation_rule(rule_id, is_active=0)

        # Validation should pass even with missing field
        metadata = {'openid_provider': {}}
        jwks = {'keys': []}
        is_valid, errors = federation_manager.validate_entity_statement('OP', metadata, jwks)

        assert is_valid is True
        assert len(errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
