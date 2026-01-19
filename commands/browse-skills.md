---
name: browse-skills
description: Browse all available Splunk Assistant skills with descriptions
---

# Browse Splunk Assistant Skills

Display all 14 available Splunk Assistant Skills with their purpose and trigger keywords.

## Skill Catalog

| Skill | Purpose | Triggers |
|-------|---------|----------|
| `splunk-assistant` | Central hub and router - routes requests to specialized skills | splunk, search, query, SPL |
| `splunk-search` | SPL query execution (oneshot, normal, blocking modes) | search, SPL, query, find, oneshot, blocking |
| `splunk-job` | Search job lifecycle (create, monitor, pause, cancel) | job, SID, status, progress, cancel, pause |
| `splunk-export` | High-volume streaming data extraction | export, download, extract, stream, ETL |
| `splunk-metadata` | Index, source, sourcetype discovery | metadata, index, source, sourcetype, fields |
| `splunk-lookup` | CSV and lookup file management | lookup, CSV, upload, lookup table |
| `splunk-kvstore` | App Key Value Store operations | kvstore, collection, key-value, persist |
| `splunk-savedsearch` | Reports and scheduled searches | saved search, report, schedule |
| `splunk-alert` | Alert triggering and monitoring | alert, trigger, notification, monitor |
| `splunk-app` | Application management | app, application, install, package |
| `splunk-security` | Token management, RBAC, ACL | token, permission, ACL, RBAC, security |
| `splunk-rest-admin` | REST API configuration access | rest, admin, config, server, settings |
| `splunk-tag` | Knowledge object tagging | tag, label, classify |
| `splunk-metrics` | Real-time metrics (mstats, mcatalog) | metrics, mstats, mcatalog, time series |

## Quick Start Commands

```bash
# Search
splunk-as search oneshot "index=main | head 10"
splunk-as search normal "index=main | stats count" --wait

# Jobs
splunk-as job list
splunk-as job status <SID>

# Metadata
splunk-as metadata indexes
splunk-as metadata sourcetypes --index main

# Administration
splunk-as admin info
splunk-as security whoami
```

## Getting More Info

Use `/skill-info <skill-name>` to see detailed documentation for a specific skill.

Example: `/skill-info splunk-search`
