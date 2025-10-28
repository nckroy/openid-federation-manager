# OpenID Federation Manager

A lightweight application to manage an OpenID Federation (draft 44) as an intermediate entity/federation operator.

## Features

- **Entity Registration**: Accept and register OpenID-enabled OP and RP entities
- **Entity Statement Fetching**: Automatically retrieve entity statements from registered entities
- **Subordinate Statements**: Generate and sign subordinate statements for registered entities
- **Federation Endpoints**: 
  - `.well-known/openid-federation` - Federation entity statement
  - `/fetch` - Fetch subordinate statements
  - `/list` - List registered entities
  - `/register` - Register new entities

## Prerequisites

### Python Version
- Python 3.8+
- pip

### Node.js Version
- Node.js 16+
- npm

## Installation

### Python Setup

```bash
cd backend/python
pip install -r requirements.txt
