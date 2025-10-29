// Copyright (c) 2025 Internet2
// Licensed under the Apache License, Version 2.0 - see LICENSE file for details

const express = require('express');
const axios = require('axios');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || 'http://localhost:5000';
const FEDERATION_NAME = process.env.FEDERATION_NAME || 'OpenID Federation Manager';

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Make config available to all templates
app.use((req, res, next) => {
    res.locals.federationName = FEDERATION_NAME;
    res.locals.apiUrl = API_URL;
    next();
});

// Routes
app.get('/', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/list`);
        res.render('index', {
            entities: response.data.entities || [],
            error: null
        });
    } catch (error) {
        console.error('Error fetching entities:', error.message);
        res.render('index', {
            entities: [],
            error: 'Unable to connect to backend API'
        });
    }
});

app.get('/entities', async (req, res) => {
    try {
        const entityType = req.query.type;
        const url = entityType
            ? `${API_URL}/list?entity_type=${entityType}`
            : `${API_URL}/list`;

        const response = await axios.get(url);
        res.render('entities', {
            entities: response.data.entities || [],
            entityType: entityType || 'all',
            error: null
        });
    } catch (error) {
        console.error('Error fetching entities:', error.message);
        res.render('entities', {
            entities: [],
            entityType: req.query.type || 'all',
            error: 'Unable to fetch entities'
        });
    }
});

app.get('/register', (req, res) => {
    res.render('register', { error: null, success: null });
});

app.post('/register', async (req, res) => {
    try {
        const { entity_id, entity_type } = req.body;

        const response = await axios.post(`${API_URL}/register`, {
            entity_id,
            entity_type
        });

        res.render('register', {
            error: null,
            success: `Successfully registered ${entity_id}`,
            result: response.data
        });
    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        console.error('Error registering entity:', errorMessage);
        res.render('register', {
            error: `Registration failed: ${errorMessage}`,
            success: null,
            formData: req.body
        });
    }
});

app.get('/entity/:entityId(*)', async (req, res) => {
    try {
        const entityId = req.params.entityId;
        // URL-encode the entity ID for the API request
        const encodedEntityId = encodeURIComponent(entityId);
        const response = await axios.get(`${API_URL}/entity/${encodedEntityId}`);

        res.render('entity-details', {
            entity: response.data,
            error: null
        });
    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        console.error('Error fetching entity details:', errorMessage);
        res.render('entity-details', {
            entity: null,
            error: `Unable to fetch entity: ${errorMessage}`
        });
    }
});

app.get('/federation', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/.well-known/openid-federation`);
        res.render('federation', {
            statement: response.data,
            error: null
        });
    } catch (error) {
        console.error('Error fetching federation statement:', error.message);
        res.render('federation', {
            statement: null,
            error: 'Unable to fetch federation statement'
        });
    }
});

// API proxy endpoints (for AJAX calls)
app.get('/api/entities', async (req, res) => {
    try {
        const entityType = req.query.type;
        const url = entityType
            ? `${API_URL}/list?entity_type=${entityType}`
            : `${API_URL}/list`;

        const response = await axios.get(url);
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json({
            error: error.response?.data?.error || error.message
        });
    }
});

app.get('/api/entity/:entityId(*)', async (req, res) => {
    try {
        const entityId = req.params.entityId;
        // URL-encode the entity ID for the API request
        const encodedEntityId = encodeURIComponent(entityId);
        const response = await axios.get(`${API_URL}/entity/${encodedEntityId}`);
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json({
            error: error.response?.data?.error || error.message
        });
    }
});

// Validation Rules Routes
app.get('/validation-rules', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/validation-rules`);
        res.render('validation-rules', {
            rules: response.data.rules || [],
            error: null
        });
    } catch (error) {
        console.error('Error fetching validation rules:', error.message);
        res.render('validation-rules', {
            rules: [],
            error: 'Unable to fetch validation rules'
        });
    }
});

app.post('/validation-rules', async (req, res) => {
    try {
        const response = await axios.post(`${API_URL}/validation-rules`, req.body);
        res.redirect('/validation-rules?success=created');
    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        const response = await axios.get(`${API_URL}/validation-rules`);
        res.render('validation-rules', {
            rules: response.data.rules || [],
            error: `Failed to create rule: ${errorMessage}`,
            formData: req.body
        });
    }
});

app.post('/validation-rules/:id/delete', async (req, res) => {
    try {
        await axios.delete(`${API_URL}/validation-rules/${req.params.id}`);
        res.redirect('/validation-rules?success=deleted');
    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        res.redirect(`/validation-rules?error=${encodeURIComponent(errorMessage)}`);
    }
});

app.post('/validation-rules/:id/toggle', async (req, res) => {
    try {
        const { is_active } = req.body;
        await axios.put(`${API_URL}/validation-rules/${req.params.id}`, {
            is_active: is_active === '1' ? 1 : 0
        });
        res.redirect('/validation-rules?success=updated');
    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        res.redirect(`/validation-rules?error=${encodeURIComponent(errorMessage)}`);
    }
});

// API proxy for validation rules
app.get('/api/validation-rules', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/validation-rules`);
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json({
            error: error.response?.data?.error || error.message
        });
    }
});

app.get('/health', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/health`);
        res.json({
            ui: 'healthy',
            backend: response.data
        });
    } catch (error) {
        res.status(500).json({
            ui: 'healthy',
            backend: 'unhealthy',
            error: error.message
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`OpenID Federation Manager UI running on http://localhost:${PORT}`);
    console.log(`Backend API: ${API_URL}`);
});

module.exports = app;
