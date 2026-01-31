# Development Guide

This document covers how to add new scripts and skills to Splunk Assistant Skills.

## Adding New Scripts

### Step-by-Step

1. Create script in `{skill}/scripts/`:

```python
#!/usr/bin/env python3
"""Brief description."""

import argparse

from splunk_as import (
    get_splunk_client,
    handle_errors,
    print_success,
    validate_spl,
)

@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description='Script description')
    args = parser.parse_args(argv)

    client = get_splunk_client()
    # Implementation
    print_success("Operation completed")

if __name__ == '__main__':
    main()
```

**Note:** The `argv` parameter enables CLI integration and testability. Always use `parser.parse_args(argv)` instead of `parser.parse_args()`.

2. Create test in `{skill}/tests/test_{script}.py`:

```python
import pytest
from unittest.mock import Mock, patch

def test_script_function():
    # Test implementation
    pass
```

3. Update `SKILL.md` with usage examples

---

## Adding New Skills

### Required Files

```
skills/new-skill/
├── SKILL.md           # Skill documentation
├── scripts/           # Python scripts
│   └── ...
├── tests/             # Unit tests
│   ├── conftest.py    # Skill-specific fixtures only (see note below)
│   └── test_*.py
├── tests/live_integration/  # Integration tests
│   ├── conftest.py    # Live test fixtures
│   └── test_*.py
└── references/        # API docs, examples
```

**Note on conftest.py**: Common fixtures (`mock_splunk_client`, `mock_config`, `temp_path`, `temp_dir`, `sample_job_response`, `sample_search_results`) are provided by the root `conftest.py`. Skill-specific conftest files should only define fixtures unique to that skill. Do not add `__init__.py` files to test directories.

### SKILL.md Template

```markdown
# splunk-new-skill

Brief description.

## Triggers

Keywords that activate this skill.

## CLI Commands

| Command | Description |
|---------|-------------|
| `newskill command` | Description of command |

## Examples

\`\`\`bash
# CLI usage
splunk-as newskill command --option value

# Get help
splunk-as newskill --help
\`\`\`

## API Endpoints

- `GET /services/endpoint` - Description
```

### Register the Skill

Skills are autodiscovered via `skills/*/SKILL.md`. Simply create your skill directory under `skills/` with a `SKILL.md` file and it will be automatically loaded.

---

## Git Commit Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(skill): add new capability
fix(client): handle timeout errors
docs: update configuration guide
test(search): add integration tests
refactor(validators): simplify logic
chore: update dependencies
```

### Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Code refactoring |
| `perf` | Performance |
| `chore` | Maintenance |

---

## Code Style

### Python Guidelines

- Use type hints for function signatures
- Follow PEP 8 style (enforced by Black)
- Keep functions focused and small
- Add docstrings for public functions

### Import Order

```python
# Standard library
import argparse
import json

# Third-party
import requests

# Local
from splunk_as import get_splunk_client
```

### Error Handling

Always use the `@handle_errors` decorator for main functions:

```python
from splunk_as import handle_errors

@handle_errors
def main():
    # Your code here
    pass
```

---

## Testing Guidelines

### Unit Tests

- Test one thing per test
- Use descriptive test names
- Mock external dependencies
- Use fixtures for common setup

### Integration Tests

- Mark with `@pytest.mark.live`
- Use `@pytest.mark.destructive` for tests that modify data
- Clean up after tests
- Use `fresh_test_data` fixture for isolation

### Running Tests

```bash
# Unit tests only
pytest skills/*/tests/ -v

# Specific skill
pytest skills/splunk-search/tests/ -v

# With coverage
pytest --cov=splunk_as --cov-report=html
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

---

## Pull Request Checklist

Before submitting a PR:

- [ ] Tests pass locally
- [ ] New code has tests
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No sensitive data committed
- [ ] SKILL.md updated (if adding features)
