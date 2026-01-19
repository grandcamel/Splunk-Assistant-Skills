# Troubleshooting Guide

This document covers common issues and their solutions when working with Splunk Assistant Skills.

## Connection Errors

### Error Message

```
ConnectionError: Failed to connect to splunk.example.com:8089
```

### Solutions

1. **Verify URL and port** in your configuration
2. **Check network/firewall access** to the Splunk management port
3. **Ensure Splunk management port is accessible** (default: 8089)
4. **Verify SSL settings** - set `SPLUNK_VERIFY_SSL=false` for self-signed certs (dev only)

---

## Authentication Failures

### Error Message

```
AuthenticationError: 401 Unauthorized
```

### Solutions

1. **Verify token is valid** and not expired
2. **Check username/password** for Basic Auth
3. **Ensure proper permissions/capabilities** for your user/token
4. **Regenerate token** if expired

---

## Search Quota Exceeded

### Error Message

```
SearchQuotaError: No available search slots
```

### Solutions

1. **Cancel unused search jobs**:
   ```bash
   splunk-as job list
   splunk-as job cancel <sid>
   ```
2. **Wait for running searches** to complete
3. **Increase search quota** in Splunk (Settings > Server settings > Search preferences)
4. **Use more efficient queries** that complete faster

---

## Timeout Errors

### Error Message

```
TimeoutError: Request timed out after 30 seconds
```

### Solutions

1. **Increase timeout** for long searches:
   ```bash
   splunk-as search blocking "index=main | stats count" --timeout 300
   ```
2. **Use async mode with polling**:
   ```bash
   splunk-as search normal "long query..." --wait
   ```
3. **Optimize SPL query** - add time bounds, limit fields
4. **Break into smaller searches** if dealing with large datasets

---

## SSL Certificate Errors

### Error Message

```
SSLError: certificate verify failed
```

### Solutions

1. **For development/testing** (not recommended for production):
   ```bash
   export SPLUNK_VERIFY_SSL="false"
   ```
2. **Add CA certificate** to your trust store
3. **Use proper SSL certificates** in production

---

## Job Not Found

### Error Message

```
NotFoundError: Search job not found
```

### Solutions

1. **Check if job expired** - jobs have a TTL
2. **Extend job TTL** before it expires:
   ```python
   set_job_ttl(client, sid, ttl=3600)
   ```
3. **Re-run the search** if job was deleted

---

## Permission Denied

### Error Message

```
AuthorizationError: 403 Forbidden
```

### Solutions

1. **Check user capabilities** in Splunk
2. **Verify app permissions** for the operation
3. **Ensure token has required roles**
4. **Contact Splunk admin** to grant necessary permissions

---

## Rate Limiting

### Error Message

```
RateLimitError: 429 Too Many Requests
```

### Solutions

1. **Wait and retry** - the client automatically retries with backoff
2. **Reduce request frequency**
3. **Batch operations** where possible
4. **Contact Splunk admin** about rate limits

---

## Common Configuration Issues

### Environment Variables Not Loading

1. Ensure variables are exported:
   ```bash
   export SPLUNK_TOKEN="..."  # Not just SPLUNK_TOKEN="..."
   ```
2. Check for typos in variable names
3. Verify shell configuration (`.bashrc`, `.zshrc`)

### Settings File Not Found

1. Create `.claude/settings.local.json` in project root
2. Copy from `.claude/settings.example.json`
3. Ensure JSON is valid (use a JSON validator)

### Wrong Splunk Instance

1. Verify `SPLUNK_SITE_URL` points to correct instance
2. Check `SPLUNK_MANAGEMENT_PORT` (default: 8089)
3. Ensure you're not mixing dev/prod credentials
