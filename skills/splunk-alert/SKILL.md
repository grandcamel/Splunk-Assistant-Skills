# splunk-alert

Alert triggering, monitoring, and notification management for Splunk.

## Purpose

Create and manage alerts, monitor triggered alerts, and configure alert actions.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List alerts | - | Read-only |
| Get alert details | - | Read-only |
| List triggered alerts | - | Read-only |
| Create alert | ⚠️ | May trigger notifications |
| Update alert | ⚠️ | Previous config lost |
| Acknowledge alert | ⚠️ | Can be re-triggered |
| Delete alert | ⚠️⚠️ | May be recoverable from backup |

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
# Create an alert
splunk-as alert create "High Error Rate" \
  "index=main sourcetype=app_logs error | stats count" \
  --alert-type "number of events" \
  --alert-comparator "greater than" \
  --alert-threshold 100 \
  --severity 4 \
  --cron "*/5 * * * *" \
  --actions email \
  --email-to ops@example.com

# List all configured alerts
splunk-as alert list --app search --count 100

# Get specific alert details
splunk-as alert get alert_12345

# List triggered alert instances with filters
splunk-as alert triggered --severity 4
splunk-as alert triggered --savedsearch "High Error Rate"
splunk-as alert triggered --app search --count 20

# Acknowledge/delete a triggered alert
splunk-as alert acknowledge alert_12345 --force
```

## Alert Configuration

### Severity Levels

- 1 = debug
- 2 = info
- 3 = warn (default)
- 4 = error
- 5 = severe
- 6 = fatal

### Alert Types

- `always` - Trigger on every scheduled execution
- `number of events` - Trigger when result count meets condition
- `number of hosts` - Trigger when host count meets condition
- `number of sources` - Trigger when source count meets condition
- `custom` - Custom alert condition

### Alert Comparators

- `greater than`
- `less than`
- `equal to`
- `not equal to`
- `drops by`
- `rises by`

### Alert Actions

- `email` - Send email notification
- `webhook` - HTTP POST to webhook URL
- `script` - Execute custom script
- Custom actions configured in Splunk

## API Endpoints

- `GET /services/alerts/fired_alerts` - List triggered alerts
- `GET /services/alerts/fired_alerts/{name}` - Get specific triggered alert
- `DELETE /services/alerts/fired_alerts/{name}` - Acknowledge/delete triggered alert
- `POST /servicesNS/nobody/{app}/saved/searches` - Create alert (via saved search)
- `GET /servicesNS/nobody/{app}/saved/searches` - List alert configurations
