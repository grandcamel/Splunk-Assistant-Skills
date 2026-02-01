# splunk-app

Splunk application management.

## Purpose

Install, uninstall, enable, disable, and manage Splunk applications.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List apps | - | Read-only |
| Get app details | - | Read-only |
| Enable app | ⚠️ | Easily reversible |
| Disable app | ⚠️ | Easily reversible |
| Install app | ⚠️⚠️ | May affect system behavior |
| Uninstall app | ⚠️⚠️⚠️ | **IRREVERSIBLE** - app files deleted |

## Triggers

- "app", "application", "install"
- "package", "addon"

## CLI Commands

| Command | Description |
|---------|-------------|
| `app list` | List installed apps |
| `app get <name>` | Get app details |
| `app install <file>` | Install app from package file (.tar.gz, .tgz, .spl) |
| `app uninstall <name>` | Remove app |
| `app enable <name>` | Enable disabled app |
| `app disable <name>` | Disable app |

## Options

| Option | Commands | Description |
|--------|----------|-------------|
| `-o`, `--output` | list, get | Output format (text, json) |
| `-n`, `--name` | install | App name (overrides name from package) |
| `--update/--no-update` | install | Update if app exists |
| `-f`, `--force` | uninstall | Skip confirmation |

## Examples

```bash
# List installed apps
splunk-as app list
splunk-as app list -o json

# Get app details
splunk-as app get search
splunk-as app get search --output json

# Install app (supports .tar.gz, .tgz, .spl formats)
splunk-as app install my_app.tgz
splunk-as app install my_app.spl --update
splunk-as app install package.tar.gz --name custom_app_name

# Uninstall app
splunk-as app uninstall my_app
splunk-as app uninstall my_app --force

# Enable app
splunk-as app enable my_app

# Disable app
splunk-as app disable my_app
```

## API Endpoints

- `GET/POST /services/apps/local` - List/Install
- `GET/POST/DELETE /services/apps/local/{name}` - CRUD
- `POST /services/apps/local/{name}/package` - Export
