# splunk-alert

Alert triggering, monitoring, and notification management for Splunk.

## Purpose

Create and manage alerts, monitor triggered alerts, and configure alert actions.

## Triggers

- "alert", "trigger", "notification"
- "monitor", "alerting"

## Scripts

| Script | Description |
|--------|-------------|
| `create_alert.py` | Create alert from saved search |
| `get_alert.py` | Get alert configuration |
| `list_alerts.py` | List configured alerts |
| `get_triggered_alerts.py` | List triggered instances |
| `acknowledge_alert.py` | Acknowledge triggered alert |

## Examples

```bash
python list_alerts.py --app search
python get_triggered_alerts.py --severity high
python acknowledge_alert.py alert_12345
```

## Alert Actions

- email, webhook, script, custom
