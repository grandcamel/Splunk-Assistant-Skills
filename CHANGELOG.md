# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0](https://github.com/grandcamel/Splunk-Assistant-Skills/compare/v1.1.0...v2.0.0) (2026-01-18)


### ⚠ BREAKING CHANGES

* Restructure plugin to be documentation and slash commands only. CLI functionality (`splunk-skill`) removed and replaced by `splunk-as` from `splunk-assistant-skills-lib>=1.0.0`.

### Features

* **plugin:** add setup command and README ([eca6bcc](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/eca6bcc635d6d3163ca7a935f8462c4f72731aca))


### Bug Fixes

* **cli:** update script paths for new plugin directory structure ([65d2bae](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/65d2baec5634055a92d89f60eb86a98ab46fb8e6))
* **scripts:** prevent password disclosure for short values ([98b25ca](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/98b25caf2580001aefc0740ea4fa4052b92bbc6e))
* **scripts:** use bash array for curl options in setup-env.sh ([6141ec2](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/6141ec2c5d879c69d3a4c43e31837b8d5de103e7))
* **tests:** add cleanup() method to SearchHelper for API consistency ([71ffc72](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/71ffc72c9d1dc6fa5ab4db8dd30f070b16010e2d))
* **tests:** add external connection singleton and improve URL parsing ([9cfee35](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/9cfee35d73c5d6ea70a2e2fe96b922ac82681d9c))
* **tests:** add security warnings and make container config env-configurable ([69a18d1](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/69a18d1afc41e681a1dc6c838fc6184975bf20dc))
* **tests:** add thread-safety to Splunk container test infrastructure ([e315cbc](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/e315cbc5d3ed9e920314e0734e1f7c67a496487e))
* **tests:** add type hints to connection parameters in test_utils ([0cf44ec](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/0cf44ecdb6e437e1835c26ee3a5694e652339604))
* **tests:** fix EventBuilder delimiter and version parsing bugs ([adc6ab8](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/adc6ab844b726cf6f95633fec5e142db34306a25))
* **tests:** improve error handling and input validation in test_utils ([08e4d57](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/08e4d5714d71465d055b3b19ca732b00819502c6))
* **tests:** improve fixtures reliability and remove dead code ([3f2261e](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/3f2261e6ecc4041390927f767e6992658ee89f85))
* **tests:** improve test_utils reliability and performance ([eec1c48](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/eec1c489746fdc62a5222cb2124740dd3b428149))
* **tests:** use safe delimiter and validate values in SPL generation ([94694eb](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/94694eb033b224506eb94df7467630acdec52007))


### Code Refactoring

* convert plugin to documentation-only, CLI moved to library ([c0edffe](https://github.com/grandcamel/Splunk-Assistant-Skills/commit/c0edffeef56967183669981392bfbde968f437ee))

## [1.1.0] - 2025-01-01

### Added

#### CLI Entry Point
- New `splunk-as` command-line interface using Click framework
- 13 command groups: search, job, export, metadata, lookup, kvstore, savedsearch, alert, app, security, admin, tag, metrics
- Global options: `--output`, `--verbose`, `--quiet`
- Install via `pip install splunk-assistant-skills-lib`

#### Script Refactoring
- All 83 scripts now use `main(argv: list[str] | None = None)` pattern
- Enables CLI integration and improved testability
- Subprocess delegation for sandbox compatibility

#### Testing
- 20 new CLI tests using Click's CliRunner
- Total tests: 355 (180 unit + 175 integration)

#### Documentation
- Updated CLAUDE.md with CLI documentation and examples
- Updated README.md with CLI installation steps
- Updated all 14 SKILL.md files with CLI syntax

### Changed
- Script signature changed from `def main():` to `def main(argv=None):`
- `parser.parse_args()` changed to `parser.parse_args(argv)`

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
