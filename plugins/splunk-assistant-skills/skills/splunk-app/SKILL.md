# splunk-app

Splunk application management.

## Purpose

Install, uninstall, enable, disable, and manage Splunk applications.

## Triggers

- "app", "application", "install"
- "package", "addon"

## Scripts

| Script | Description |
|--------|-------------|
| `list_apps.py` | List installed apps |
| `get_app.py` | Get app details |
| `install_app.py` | Install app from file |
| `uninstall_app.py` | Remove app |
| `enable_app.py` | Enable disabled app |
| `disable_app.py` | Disable app |

## Examples

```bash
# List installed apps
splunk-skill app list

# Get app details
splunk-skill app get search

# Install app
splunk-skill app install my_app.tgz

# Uninstall app
splunk-skill app uninstall my_app

# Enable app
splunk-skill app enable my_app

# Disable app
splunk-skill app disable my_app
```

## API Endpoints

- `GET/POST /services/apps/local` - List/Install
- `GET/POST/DELETE /services/apps/local/{name}` - CRUD
- `POST /services/apps/local/{name}/package` - Export
