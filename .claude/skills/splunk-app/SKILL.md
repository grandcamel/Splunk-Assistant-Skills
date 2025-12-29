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
python list_apps.py
python get_app.py search
python install_app.py my_app.tgz
```

## API Endpoints

- `GET/POST /services/apps/local` - List/Install
- `GET/POST/DELETE /services/apps/local/{name}` - CRUD
- `POST /services/apps/local/{name}/package` - Export
