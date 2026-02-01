# Testing Guide

This document covers testing for Splunk Assistant Skills.

## Overview

Splunk Assistant Skills is a Claude Code plugin consisting of markdown skill files that reference the `splunk-as` CLI. The plugin itself has no custom Python code requiring unit tests.

## Test Types

| Type | Location | Purpose |
|------|----------|---------|
| E2E Tests | `tests/e2e/` | Validate plugin with Claude Code CLI |
| Unit Tests | [splunk-as](https://github.com/grandcamel/splunk-as) | Library code tests |
| Live Integration | [splunk-as](https://github.com/grandcamel/splunk-as) | Splunk API tests |

## E2E Tests

End-to-end tests validate the plugin works correctly with the Claude Code CLI.

### Prerequisites

**Authentication (choose one):**

```bash
# Option 1: API Key
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: OAuth
claude auth login
```

### Running E2E Tests

```bash
# Run all tests
./scripts/run-e2e-tests.sh

# Run locally (no Docker)
./scripts/run-e2e-tests.sh --local

# Verbose output
./scripts/run-e2e-tests.sh --verbose

# Debug shell
./scripts/run-e2e-tests.sh --shell
```

See [tests/e2e/README.md](../tests/e2e/README.md) for details.

## Library Tests

Unit tests and live integration tests for the `splunk-as` library are in the [splunk-as repository](https://github.com/grandcamel/splunk-as):

```bash
cd /path/to/splunk-as

# Unit tests
pytest tests/ -v

# Live integration tests (requires Splunk)
pytest tests/live/ --live -v
```

## CI/CD Integration

The project includes GitHub Actions workflows:

- `.github/workflows/validate.yml` - Runs linting and doc validation on push/PR
- `.github/workflows/release.yml` - Creates releases with linting gates
