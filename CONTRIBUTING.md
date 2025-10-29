# Contributing to OpenID Federation Manager

Thank you for your interest in contributing to the OpenID Federation Manager! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Submitting Changes](#submitting-changes)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows professional open source standards. Please be respectful, constructive, and collaborative in all interactions.

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- Git
- Docker Desktop (optional, for devcontainer)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/openid-federation-manager.git
   cd openid-federation-manager
   ```

3. **Add the upstream repository:**
   ```bash
   git remote add upstream https://github.com/nckroy/openid-federation-manager.git
   ```

4. **Set up development environment:**

   **Option A: Using Dev Container (Recommended)**
   ```bash
   # Open in VS Code and reopen in container
   code .
   # Press F1 → "Dev Containers: Reopen in Container"
   ```

   **Option B: Local Setup**
   ```bash
   # Install backend dependencies
   cd backend/python
   pip install -r requirements.txt

   # Install frontend dependencies
   cd ../../frontend
   npm install
   ```

## Development Workflow

### Branch Naming Convention

Use descriptive branch names with the following prefixes:

- `feature/` - New features (e.g., `feature/trust-marks`)
- `fix/` - Bug fixes (e.g., `fix/validation-error`)
- `docs/` - Documentation updates (e.g., `docs/api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/database-layer`)

### Creating a Feature Branch

```bash
# Ensure main is up to date
git checkout main
git pull upstream main

# Create your feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your code changes
2. Write or update tests
3. Update documentation as needed
4. Test your changes thoroughly
5. Commit with clear, descriptive messages

### Keeping Your Branch Updated

```bash
# Fetch latest changes from upstream
git fetch upstream

# Rebase your branch on latest main
git rebase upstream/main

# If conflicts occur, resolve them and continue
git rebase --continue
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Use Black for code formatting: `black backend/python/`
- Use Flake8 for linting: `flake8 backend/python/`
- Maximum line length: 100 characters

**Example:**
```python
def validate_entity(entity_id: str, entity_type: str) -> Tuple[bool, List[str]]:
    """
    Validate an entity against configured rules.

    Args:
        entity_id: The entity's unique identifier
        entity_type: Either 'OP' or 'RP'

    Returns:
        Tuple of (is_valid, error_messages)
    """
    # Implementation here
```

### JavaScript (Frontend)

- Use ES6+ syntax
- Use `const` and `let` (avoid `var`)
- Use async/await for asynchronous operations
- 2-space indentation
- Semicolons required
- Clear variable and function names

**Example:**
```javascript
async function fetchValidationRules() {
  try {
    const response = await fetch('/api/validation-rules');
    const data = await response.json();
    return data.rules;
  } catch (error) {
    console.error('Failed to fetch rules:', error);
    throw error;
  }
}
```

### File Headers

All source files must include the Apache License header:

```python
# Copyright (c) 2025 Internet2
# Licensed under the Apache License, Version 2.0 - see LICENSE file for details
```

## Testing Requirements

### Running Tests

**Backend Tests:**
```bash
# Run all backend tests
python3 -m pytest tests/backend/ -v

# Run specific test file
python3 -m pytest tests/backend/test_validation_rules.py -v

# Run with coverage
python3 -m pytest tests/backend/ --cov=backend/python --cov-report=html
```

**Frontend Tests:**
```bash
cd tests/frontend
npm install
npm test
```

**Integration Tests:**
```bash
cd tests/integration
python3 test_full_stack.py
```

### Test Requirements

- All new features must include unit tests
- Aim for >80% code coverage
- Tests must pass before submitting PR
- Include both positive and negative test cases
- Test edge cases and error conditions

### Writing Tests

**Python Example:**
```python
def test_create_validation_rule(self, federation_manager):
    """Test creating a validation rule"""
    success = federation_manager.create_validation_rule(
        rule_name="test_rule",
        entity_type="OP",
        field_path="metadata.openid_provider.issuer",
        validation_type="required"
    )

    assert success is True
    rules = federation_manager.get_validation_rules()
    assert len(rules) == 1
```

## Submitting Changes

### Commit Messages

Write clear, descriptive commit messages:

**Format:**
```
Brief summary of changes (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how.

- Use bullet points for multiple changes
- Reference issues: Fixes #123, Relates to #456
```

**Example:**
```
Add validation rule for HTTPS enforcement

Implement a new validation rule type that ensures all OP issuer
URLs use HTTPS protocol. This improves federation security by
preventing insecure HTTP connections.

- Add regex validation type
- Update validation engine
- Add tests for HTTPS validation

Fixes #42
```

### Pre-Commit Checklist

Before pushing your changes:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (README, CLAUDE.md, docstrings)
- [ ] No debugging code or console logs left in
- [ ] Commit messages are clear and descriptive
- [ ] Branch is rebased on latest main

## Pull Request Process

### Creating a Pull Request

1. **Push your branch to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub:**
   - Go to the upstream repository
   - Click "Pull requests" → "New pull request"
   - Click "compare across forks"
   - Select your fork and branch
   - Fill out the PR template completely

3. **PR Title Format:**
   ```
   [Feature/Fix/Docs] Brief description of changes
   ```
   Examples:
   - `[Feature] Add trust marks support`
   - `[Fix] Resolve validation rule edge case`
   - `[Docs] Update API documentation`

### PR Description Template

Your PR should include:

- **Summary**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Changes**: What was changed?
- **Testing**: How was this tested?
- **Breaking Changes**: Any breaking changes?
- **Screenshots**: For UI changes
- **Related Issues**: Links to related issues

### Review Process

1. **Automated Checks**: All tests must pass
2. **Code Review**: Maintainer will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Maintainer approves the PR
5. **Merge**: Maintainer merges using squash and merge

### After Your PR is Merged

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Delete your feature branch
git branch -d feature/your-feature-name

# Optionally delete remote branch
git push origin --delete feature/your-feature-name
```

## Project Structure

```
openid-federation-manager/
├── backend/python/          # Flask API backend
├── frontend/                # Express web UI
├── config/                  # Configuration files
├── database/                # Database schema
├── tests/                   # Test suites
│   ├── backend/            # Backend tests
│   ├── frontend/           # Frontend tests
│   └── integration/        # End-to-end tests
└── .devcontainer/          # Dev container config
```

## Getting Help

- **Documentation**: See README.md and CLAUDE.md
- **Issues**: Check existing issues on GitHub
- **Questions**: Open a discussion on GitHub

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to OpenID Federation Manager!**

Copyright (c) 2025 Internet2
