// Copyright (c) 2025 Internet2
// Licensed under the Apache License, Version 2.0 - see LICENSE file for details

const chai = require('chai');
const chaiHttp = require('chai-http');
const expect = chai.expect;

chai.use(chaiHttp);

// Mock the backend API
const nock = require('nock');
const API_URL = process.env.API_URL || 'http://localhost:5000';

describe('Frontend Server', function() {
    let app;
    let server;

    before(function(done) {
        // Load the app
        process.env.API_URL = API_URL;
        app = require('../../frontend/server');
        done();
    });

    after(function() {
        if (server) {
            server.close();
        }
    });

    describe('GET /', function() {
        it('should return dashboard page', function(done) {
            // Mock backend response
            nock(API_URL)
                .get('/list')
                .reply(200, { entities: [] });

            chai.request(app)
                .get('/')
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Dashboard');
                    done();
                });
        });

        it('should handle backend API errors gracefully', function(done) {
            // Mock backend error
            nock(API_URL)
                .get('/list')
                .replyWithError('Connection failed');

            chai.request(app)
                .get('/')
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Unable to connect');
                    done();
                });
        });
    });

    describe('GET /entities', function() {
        it('should return entities page', function(done) {
            nock(API_URL)
                .get('/list')
                .reply(200, {
                    entities: [
                        {
                            entity_id: 'https://test.example.com',
                            entity_type: 'OP',
                            status: 'active',
                            registered_at: '2025-01-01T00:00:00',
                            last_updated: '2025-01-01T00:00:00'
                        }
                    ]
                });

            chai.request(app)
                .get('/entities')
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Registered Entities');
                    expect(res.text).to.include('test.example.com');
                    done();
                });
        });

        it('should filter entities by type', function(done) {
            nock(API_URL)
                .get('/list?entity_type=OP')
                .reply(200, { entities: [] });

            chai.request(app)
                .get('/entities?type=OP')
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Registered Entities');
                    done();
                });
        });
    });

    describe('GET /register', function() {
        it('should return registration form', function(done) {
            chai.request(app)
                .get('/register')
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Register New Entity');
                    expect(res.text).to.include('entity_id');
                    expect(res.text).to.include('entity_type');
                    done();
                });
        });
    });

    describe('POST /register', function() {
        it('should handle successful registration', function(done) {
            nock(API_URL)
                .post('/register', {
                    entity_id: 'https://test.example.com',
                    entity_type: 'OP'
                })
                .reply(201, {
                    status: 'registered',
                    entity_id: 'https://test.example.com',
                    fetch_endpoint: API_URL + '/fetch?sub=https://test.example.com'
                });

            chai.request(app)
                .post('/register')
                .type('form')
                .send({
                    entity_id: 'https://test.example.com',
                    entity_type: 'OP'
                })
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Successfully registered');
                    done();
                });
        });

        it('should handle registration errors', function(done) {
            nock(API_URL)
                .post('/register')
                .reply(400, { error: 'Invalid entity' });

            chai.request(app)
                .post('/register')
                .type('form')
                .send({
                    entity_id: 'https://invalid.example.com',
                    entity_type: 'OP'
                })
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Registration failed');
                    done();
                });
        });
    });

    describe('GET /entity/:entityId', function() {
        it('should return entity details', function(done) {
            const entityId = 'https://test.example.com';

            nock(API_URL)
                .get('/entity/' + entityId)
                .reply(200, {
                    entity_id: entityId,
                    entity_type: 'OP',
                    status: 'active',
                    registered_at: '2025-01-01T00:00:00',
                    last_updated: '2025-01-01T00:00:00',
                    metadata: '{"issuer":"' + entityId + '"}',
                    jwks: '{"keys":[]}'
                });

            chai.request(app)
                .get('/entity/' + entityId)
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Entity Details');
                    expect(res.text).to.include(entityId);
                    done();
                });
        });

        it('should handle entity not found', function(done) {
            nock(API_URL)
                .get('/entity/https://notfound.example.com')
                .reply(404, { error: 'Entity not found' });

            chai.request(app)
                .get('/entity/https://notfound.example.com')
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.text).to.include('Unable to fetch entity');
                    done();
                });
        });
    });

    describe('GET /health', function() {
        it('should return health status', function(done) {
            nock(API_URL)
                .get('/health')
                .reply(200, { status: 'healthy' });

            chai.request(app)
                .get('/health')
                .end(function(err, res) {
                    expect(res).to.have.status(200);
                    expect(res.body).to.have.property('ui');
                    expect(res.body).to.have.property('backend');
                    expect(res.body.ui).to.equal('healthy');
                    done();
                });
        });

        it('should handle backend unhealthy', function(done) {
            nock(API_URL)
                .get('/health')
                .replyWithError('Backend unavailable');

            chai.request(app)
                .get('/health')
                .end(function(err, res) {
                    expect(res).to.have.status(500);
                    expect(res.body.ui).to.equal('healthy');
                    expect(res.body.backend).to.equal('unhealthy');
                    done();
                });
        });
    });
});
