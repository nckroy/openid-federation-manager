-- Copyright (c) 2025 Internet2
-- Licensed under the MIT License - see LICENSE file for details

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

CREATE INDEX IF NOT EXISTS idx_entity_id ON entities(entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_statement_subject ON entity_statements(subject);
CREATE INDEX IF NOT EXISTS idx_statement_expires ON entity_statements(expires_at);
