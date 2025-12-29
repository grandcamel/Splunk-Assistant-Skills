# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Features

- Initial release of Splunk Assistant Skills
- **splunk-assistant**: Hub/router skill with progressive disclosure
- **splunk-job**: Search job lifecycle orchestration
- **splunk-search**: SPL query execution in multiple modes
- **splunk-export**: High-volume streaming data extraction
- **splunk-metadata**: Index, source, sourcetype discovery
- **splunk-lookup**: CSV and lookup file management
- **splunk-tag**: Knowledge object tagging
- **splunk-savedsearch**: Reports and scheduled searches
- **splunk-rest-admin**: REST API configuration access
- **splunk-security**: Token management and RBAC
- **splunk-metrics**: Real-time metrics (mstats, mcatalog)
- **splunk-alert**: Alert triggering and monitoring
- **splunk-app**: Application management
- **splunk-kvstore**: App Key Value Store

### Shared Library

- `splunk_client.py`: HTTP client with dual auth (Bearer/Basic) and retry logic
- `config_manager.py`: Multi-source configuration with profile support
- `error_handler.py`: Comprehensive exception hierarchy
- `validators.py`: Splunk-specific input validation
- `formatters.py`: Output formatting utilities
- `spl_helper.py`: SPL query building and parsing
- `job_poller.py`: Async job state polling
- `time_utils.py`: Splunk time modifier handling
