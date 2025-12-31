# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0](https://github.com/grandcamel/Splunk-Assistant-Skills/compare/v1.0.0...v1.1.0) (2025-12-31)


### Features

* **cli:** add splunk-skill CLI entry point with Click framework ([b180858](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/b180858520442299f5f2b1901ab61fd0d6f713e3))


### Bug Fixes

* **tests:** implement singleton container with reference counting ([1513231](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/15132317725a05be4a1b3e4b0c7d59e2e872c00c))

## [1.0.0] - 2024-12-29

### Added

#### Plugin Marketplace
- Plugin marketplace for Claude Code distribution
- `plugin.json` manifests for all 14 skills
- Installation via `/plugin marketplace add grandcamel/Splunk-Assistant-Skills`

#### Skills (14 total)
- **splunk-assistant** - Hub router with 3-level progressive disclosure
- **splunk-search** - SPL query execution (oneshot/normal/blocking modes)
- **splunk-job** - Search job lifecycle management
- **splunk-export** - High-volume streaming data extraction
- **splunk-metadata** - Index, source, sourcetype discovery
- **splunk-lookup** - CSV and lookup file management
- **splunk-tag** - Knowledge object tagging
- **splunk-savedsearch** - Reports and scheduled searches
- **splunk-rest-admin** - REST API configuration access
- **splunk-security** - Token management and RBAC
- **splunk-metrics** - Real-time metrics (mstats, mcatalog)
- **splunk-alert** - Alert triggering and monitoring
- **splunk-app** - Application management
- **splunk-kvstore** - App Key Value Store operations

#### Shared Library
- `splunk_client.py` - HTTP client with retry and dual auth (Bearer/Basic)
- `config_manager.py` - Multi-source configuration with profile support
- `error_handler.py` - Custom exception hierarchy
- `validators.py` - Input validation utilities
- `formatters.py` - Output formatting helpers
- `spl_helper.py` - SPL query building/parsing
- `job_poller.py` - Async job polling with progress callbacks
- `time_utils.py` - Splunk time modifier handling

#### Testing
- 73 unit tests for shared library
- 175 live integration tests across 11 skills
- Docker-based testing with Splunk container
- Test markers: `@pytest.mark.live`, `@pytest.mark.destructive`, `@pytest.mark.slow`

#### Documentation
- Comprehensive CLAUDE.md with full API reference
- SKILL.md documentation for each skill
- README with quick start and use cases

### Technical Highlights
- Dual authentication (JWT Bearer preferred, Basic Auth fallback)
- Multi-profile configuration (dev/staging/production)
- 4-layer error handling with custom exceptions
- Type-safe with full annotations

## [Unreleased]

### Planned
- Splunk Cloud native API support
- Dashboard management skills
- Data model query skills
- Federated search capabilities
- Workflow action triggers

---

[1.0.0]: https://github.com/grandcamel/Splunk-Assistant-Skills/releases/tag/v1.0.0
[Unreleased]: https://github.com/grandcamel/Splunk-Assistant-Skills/compare/v1.0.0...HEAD
