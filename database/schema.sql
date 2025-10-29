-- Copyright (c) 2025 Internet2
-- Licensed under the Apache License, Version 2.0 - see LICENSE file for details

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT UNIQUE NOT NULL,
    entity_type TEXT NOT NULL CHECK(entity_type IN ('OP', 'RP')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'active', 'suspended', 'revoked')),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    jwks TEXT,
    authority_hints TEXT,
    trust_marks TEXT
);

CREATE TABLE IF NOT EXISTS entity_statements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    issuer TEXT NOT NULL,
    subject TEXT NOT NULL,
    statement TEXT NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);

CREATE TABLE IF NOT EXISTS federation_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signing_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kid TEXT UNIQUE NOT NULL,
    key_type TEXT NOT NULL,
    private_key TEXT NOT NULL,
    public_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS validation_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT UNIQUE NOT NULL,
    entity_type TEXT NOT NULL CHECK(entity_type IN ('OP', 'RP', 'BOTH')),
    field_path TEXT NOT NULL,
    validation_type TEXT NOT NULL CHECK(validation_type IN ('required', 'exact_value', 'regex', 'range', 'exists')),
    validation_value TEXT,
    error_message TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_entity_id ON entities(entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_statement_subject ON entity_statements(subject);
CREATE INDEX IF NOT EXISTS idx_statement_expires ON entity_statements(expires_at);
CREATE INDEX IF NOT EXISTS idx_validation_entity_type ON validation_rules(entity_type);
CREATE INDEX IF NOT EXISTS idx_validation_active ON validation_rules(is_active);
