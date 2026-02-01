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

## CLI Commands

| Command | Description |
|---------|-------------|
| `alert create` | Create a new alert |
| `alert get` | Get alert details |
| `alert list` | List all alerts (scheduled searches with alert actions) |
| `alert triggered` | List triggered alerts |
| `alert acknowledge` | Acknowledge a triggered alert |

## Examples

```bash
# Create an alert
splunk-as alert create --name "High Error Rate" \
  --search "index=main sourcetype=app_logs error | stats count" \
  --condition "number of events" \
  --comparator "greater than" \
  --threshold 100 \
  --cron "*/5 * * * *" \
  --actions email \
  --email-to ops@example.com

# List all configured alerts
splunk-as alert list --app search --count 100

# Get specific alert details
splunk-as alert get "High Error Rate"

# List triggered alert instances with filters
splunk-as alert triggered --app search --count 20

# Acknowledge/delete a triggered alert
splunk-as alert acknowledge alert_12345
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
