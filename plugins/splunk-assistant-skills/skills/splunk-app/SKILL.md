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
splunk-as app list

# Get app details
splunk-as app get search

# Install app
splunk-as app install my_app.tgz

# Uninstall app
splunk-as app uninstall my_app

# Enable app
splunk-as app enable my_app

# Disable app
splunk-as app disable my_app
```

## API Endpoints

- `GET/POST /services/apps/local` - List/Install
- `GET/POST/DELETE /services/apps/local/{name}` - CRUD
- `POST /services/apps/local/{name}/package` - Export
