# Development Guide

This document covers how to add and modify skills in Splunk Assistant Skills.

## Overview

Splunk Assistant Skills is a Claude Code plugin consisting of markdown skill files. Skills document how to use the `splunk-as` CLI commands for various Splunk operations.

## Adding New Skills

### Required Files

```
skills/new-skill/
├── SKILL.md           # Skill documentation (required)
└── references/        # API docs, examples (optional)
```

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
fix(docs): correct command syntax
docs: update configuration guide
chore: update dependencies
```

### Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `chore` | Maintenance |

---

## Code Style

### Markdown Guidelines

- Use consistent heading levels
- Include code examples with proper syntax highlighting
- Keep CLI examples accurate and tested
- Document all command flags and options

### Linting

```bash
# Check formatting
make lint

# Fix formatting issues
make lint-fix
```

---

## Testing

### E2E Tests

E2E tests validate the plugin works with Claude Code CLI:

```bash
./scripts/run-e2e-tests.sh
```

### Library Development

If you need to modify the `splunk-as` library itself, see the [splunk-as repository](https://github.com/grandcamel/splunk-as).

See [TESTING.md](TESTING.md) for detailed testing documentation.

---

## Pull Request Checklist

Before submitting a PR:

- [ ] Linting passes (`make lint`)
- [ ] Documentation is accurate
- [ ] CLI examples are tested
- [ ] Commit messages follow conventions
- [ ] SKILL.md updated (if adding features)
