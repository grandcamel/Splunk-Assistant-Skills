---
name: splunk-discover-instance
description: Discover Splunk deployment type, version, and capabilities
---

# Splunk Instance Discovery

Discover and display information about the connected Splunk instance.

## Discovery Steps

### Step 1: Verify Connection

Check connectivity to the Splunk Search Head on management port 8089:

```bash
splunk-as admin info
```

This returns:
- Server version and build
- Deployment type (Cloud vs on-prem)
- Connection status
- Current user and capabilities

### Step 2: Check Server Health

```bash
splunk-as admin health
```

### Step 3: List Available Indexes

```bash
splunk-as metadata indexes
```

### Step 4: Check User Permissions

```bash
splunk-as security whoami
```

## Expected Output

After running discovery, summarize:

1. **Connection Status**: Connected/Not Connected
2. **Splunk Version**: e.g., 9.1.0
3. **Deployment Type**: Splunk Enterprise, Splunk Cloud, etc.
4. **Current User**: Username and roles
5. **Available Indexes**: List of accessible indexes
6. **Key Capabilities**: What operations are permitted

## Troubleshooting

If connection fails:
- Verify `SPLUNK_SITE_URL` environment variable is set
- Check `SPLUNK_TOKEN` or `SPLUNK_USERNAME`/`SPLUNK_PASSWORD`
- Ensure port 8089 is accessible
- Run `/assistant-skills-setup` to reconfigure
