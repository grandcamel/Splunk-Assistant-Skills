# Skill Routing Decision Tree

This guide helps route requests to the appropriate Splunk skill.

## Quick Decision Flowchart

```
                         [User Request]
                              |
              +---------------+---------------+
              |                               |
        [Has SPL query?]               [No SPL query]
              |                               |
              v                               v
    +-------------------+          +--------------------+
    | splunk-search     |          | What resource?     |
    | (oneshot/normal/  |          +--------------------+
    |  blocking)        |                    |
    +-------------------+          +---------+---------+
                                   |         |         |
                              [Data]    [Config]   [Admin]
                                   |         |         |
                        +----------+    +----+----+   +----------+
                        |               |         |              |
                    [Job?]         [Saved]    [App?]      [Security?]
                        |          [Search?]     |              |
                        v              |         v              v
                 splunk-job            v    splunk-app   splunk-security
                        |       splunk-savedsearch
               +--------+--------+
               |                 |
          [Export?]         [Metadata?]
               |                 |
               v                 v
         splunk-export    splunk-metadata
```

## Keyword Routing Table

| Keywords | Route To | Confidence |
|----------|----------|------------|
| search, query, SPL, find, execute | splunk-search | High |
| job, SID, status, poll, cancel, pause | splunk-job | High |
| export, download, stream, large, ETL | splunk-export | High |
| index, source, sourcetype, metadata, fields | splunk-metadata | High |
| lookup, CSV, upload, enrichment | splunk-lookup | High |
| tag, label, classify | splunk-tag | High |
| saved search, report, schedule, scheduled | splunk-savedsearch | High |
| alert, trigger, notification, monitor | splunk-alert | High |
| token, permission, ACL, RBAC, capability | splunk-security | High |
| metrics, mstats, mcatalog, time series | splunk-metrics | High |
| app, application, install, addon | splunk-app | High |
| kvstore, collection, key-value, persist | splunk-kvstore | High |
| rest, admin, config, server info | splunk-rest-admin | High |
| connect, verify, authenticate | splunk-assistant | High |

## Operation Verb Mapping

| Verb | Typical Skills | Notes |
|------|----------------|-------|
| get, list, show, view | All skills | Read-only operations |
| search, query, find | splunk-search | SPL execution |
| create, add, insert | splunk-savedsearch, splunk-lookup, splunk-kvstore, splunk-alert | Write operations |
| update, modify, edit | splunk-savedsearch, splunk-kvstore, splunk-tag | Modification operations |
| delete, remove | All skills with CRUD | Destructive operations |
| export, download | splunk-export, splunk-lookup | Data extraction |
| upload | splunk-lookup, splunk-app | Data ingestion |
| cancel, pause, stop | splunk-job | Job control |
| enable, disable | splunk-savedsearch, splunk-app | Toggle operations |

## Resource Type Signals

| Resource Type | Signal Words | Primary Skill | Secondary |
|--------------|--------------|---------------|-----------|
| Search Job | SID, job ID, 1234567890.12345 | splunk-job | splunk-search |
| Saved Search | report, scheduled, dashboard | splunk-savedsearch | splunk-alert |
| Lookup | CSV, lookup table, enrichment | splunk-lookup | - |
| KV Store | collection, key, record | splunk-kvstore | - |
| Alert | fired, triggered, notification | splunk-alert | splunk-savedsearch |
| App | package, addon, .tgz | splunk-app | - |
| Token | JWT, bearer, credential | splunk-security | - |
| Index | bucket, event count | splunk-metadata | - |

## Ambiguous Request Handling

### Request: "Show me the data"
1. Ask: "Do you want to search for data (splunk-search) or explore what data exists (splunk-metadata)?"
2. If time-bounded: likely splunk-search
3. If discovery-focused: likely splunk-metadata

### Request: "Create a report"
1. If one-time: splunk-search with export
2. If recurring/scheduled: splunk-savedsearch
3. If alerting needed: splunk-alert

### Request: "Delete the job"
1. If SID provided: splunk-job delete
2. If name provided: likely splunk-savedsearch delete
3. Ask for clarification if ambiguous

### Request: "Upload the file"
1. If CSV for enrichment: splunk-lookup
2. If app package: splunk-app
3. Ask: "Is this a lookup CSV or an app package?"

### Request: "Get the status"
1. Server status: splunk-rest-admin
2. Job status: splunk-job
3. Alert status: splunk-alert
4. Ask: "Status of what - server, job, or alert?"

## Multi-Skill Workflows

### ETL Pipeline
1. splunk-search - Create the search job
2. splunk-job - Monitor progress
3. splunk-export - Stream results to file

### Alert Setup
1. splunk-savedsearch - Create base search
2. splunk-alert - Configure alert conditions
3. splunk-security - Set permissions

### Data Enrichment
1. splunk-lookup - Upload CSV
2. splunk-search - Test with lookup command
3. splunk-metadata - Verify field extraction

## Routing Priority

When multiple skills match:
1. **Most specific match wins** - "cancel job" -> splunk-job, not splunk-search
2. **Explicit resource beats action** - "delete saved search" -> splunk-savedsearch
3. **Context from conversation** - Recent job creation -> splunk-job for status
4. **User's stated intent** - Always respect explicit skill requests
