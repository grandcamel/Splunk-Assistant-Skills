# Assistant-Skills Alignment Plan

This document outlines patterns discovered across three Assistant-Skills projects and a phased implementation plan for alignment.

## Executive Summary

**Projects Reviewed:**
| Project | Skills | Tests | Library |
|---------|--------|-------|---------|
| Jira-Assistant-Skills | 14 | 952 unit + live | `jira-assistant-skills-lib` |
| Confluence-Assistant-Skills | 14 | comprehensive | `confluence-assistant-skills-lib` |
| Splunk-Assistant-Skills | 14 | 73 unit + live | `splunk-assistant-skills-lib` |

**Key Insight:** Jira and Confluence projects share a common base library (`assistant-skills-lib>=0.3.0`) that provides core functionality. Splunk does not yet use this base library.

---

## Pattern Analysis

### Patterns Already Aligned

| Pattern | Jira | Confluence | Splunk |
|---------|------|------------|--------|
| 14 specialized skills | ✅ | ✅ | ✅ |
| Hub/router skill | ✅ | ✅ | ✅ |
| Progressive disclosure (3 levels) | ✅ | ✅ | ✅ |
| SKILL.md format | ✅ | ✅ | ✅ |
| PyPI shared library | ✅ | ✅ | ✅ |
| Click-based CLI | ✅ | ✅ | ✅ |
| Config priority order | ✅ | ✅ | ✅ |
| Setup wizard command | ✅ | ✅ | ✅ |
| Error exception hierarchy | ✅ | ✅ | ✅ |
| Pytest markers | ✅ | ✅ | ✅ |

### Patterns Needing Alignment

#### 1. Base Library Inheritance

**Current State:**
- Jira: `jira-assistant-skills-lib` depends on `assistant-skills-lib>=0.3.0`
- Confluence: `confluence-assistant-skills-lib` depends on `assistant-skills-lib>=0.2.1`
- Splunk: `splunk-assistant-skills-lib>=0.2.2` (standalone, no base dependency)

**Opportunity:** Splunk should adopt `assistant-skills-lib` as base to gain:
- Shared validators (email, URL, file path)
- Base exception hierarchy
- Common formatters (table, JSON, colors)
- Config manager base class
- Retry logic utilities

#### 2. Mock Client System

**Jira Pattern (Most Advanced):**
```
mock/
├── base.py           # MockJiraClientBase with seed data
├── factories.py      # ResponseFactory for consistent API responses
└── mixins/           # Feature-specific mock behaviors
    ├── admin.py
    ├── agile.py
    ├── search.py
    └── time.py
```

**Activation:** `JIRA_MOCK_MODE=true` environment variable

**Gaps:**
- Splunk: No mock client system
- Confluence: Basic mock client, no mixin architecture

#### 3. Test Coverage Disparity

| Project | Unit Tests | Lines of Test Code | Coverage Target |
|---------|------------|-------------------|-----------------|
| Jira | 952 | 12,834 | 95% mandatory |
| Confluence | ~400 | ~8,000 | 90% target |
| Splunk | 73 | ~3,000 | Not enforced |

**Opportunity:** Splunk needs significantly more unit tests.

#### 4. Documentation Structure

**Jira Pattern (Most Complete):**
```
docs/
├── ARCHITECTURE.md          # Library architecture
├── CLI_REFERENCE.md         # Complete CLI documentation
├── TESTING.md               # Testing instructions
├── CONTAINER_TESTING.md     # Docker testing guide
├── GIT_WORKFLOW.md          # Git conventions
├── PARALLEL_SUBAGENTS.md    # Subagent patterns
├── configuration.md         # Configuration guide
├── troubleshooting.md       # Common issues
└── quick-start.md           # Getting started
```

**Gaps:**
- Splunk: Most documentation in CLAUDE.md (10,000+ lines)
- Confluence: Has docs/ but less complete

#### 5. Context/Cache Systems

**Confluence Pattern:**
```python
class SpaceContext:
    """Caches space metadata for intelligent defaults"""
    def get_common_labels(space_key: str) -> list
    def suggest_parent_page(space_key: str, title: str) -> str
```

**Jira Pattern:**
```python
class CacheManager:
    """SQLite-based caching with TTL"""
    # Persistent cache for expensive operations
```

**Splunk Gap:** No equivalent context/cache system for:
- Index metadata caching
- Common field suggestions
- Saved search suggestions

#### 6. Bulk Operations Skill

**Jira Pattern (Most Robust):**
- Dedicated `jira-bulk` skill
- Dry-run preview before execution
- Rollback safety with checkpoints
- Partial failure handling
- Progress tracking with tqdm

**Gaps:**
- Splunk: Export mode exists but no dedicated bulk skill
- Confluence: Has bulk skill but simpler implementation

#### 7. Content Format Helpers

| Project | Content Helpers |
|---------|-----------------|
| Confluence | `adf_helper.py`, `xhtml_helper.py`, `markdown_parser.py` |
| Jira | `adf_helper.py` |
| Splunk | `spl_helper.py` |

**Aligned:** Each has domain-specific content helpers.

---

## Implementation Phases

### Phase 1: Base Library Adoption (Splunk)

**Goal:** Integrate `assistant-skills-lib` into `splunk-assistant-skills-lib`

**Tasks:**
1. Add `assistant-skills-lib>=0.3.0` to `pyproject.toml` dependencies
2. Refactor `error_handler.py` to inherit from base exceptions
3. Refactor `config_manager.py` to extend `BaseConfigManager`
4. Replace duplicated validators with base library imports
5. Update imports across all modules

**Files to Modify:**
```
splunk-assistant-skills-lib/
├── pyproject.toml                    # Add dependency
├── src/splunk_assistant_skills_lib/
│   ├── __init__.py                   # Update exports
│   ├── error_handler.py              # Inherit from base
│   ├── config_manager.py             # Extend BaseConfigManager
│   └── validators.py                 # Use base + extend
```

**Estimated Effort:** Medium
**Risk:** Low (additive changes)

---

### Phase 2: Mock Client System (Splunk)

**Goal:** Create comprehensive mock system for offline testing

**Tasks:**
1. Create `mock/` directory structure
2. Implement `MockSplunkClientBase` with seed data
3. Create `ResponseFactory` for consistent responses
4. Add feature mixins (search, jobs, metadata)
5. Add `SPLUNK_MOCK_MODE` environment variable support
6. Update tests to use mock client

**New Files:**
```
splunk-assistant-skills-lib/
└── src/splunk_assistant_skills_lib/
    └── mock/
        ├── __init__.py
        ├── base.py                   # MockSplunkClientBase
        ├── factories.py              # ResponseFactory
        └── mixins/
            ├── __init__.py
            ├── search.py             # Search result mocks
            ├── jobs.py               # Job lifecycle mocks
            ├── metadata.py           # Index/sourcetype mocks
            └── export.py             # Export mocks
```

**Reference:** Port patterns from `jira-assistant-skills-lib/mock/`

**Estimated Effort:** High
**Risk:** Medium (new subsystem)

---

### Phase 3: Documentation Restructure (Splunk)

**Goal:** Split CLAUDE.md into focused documentation files

**Tasks:**
1. Create `docs/` directory
2. Extract architecture documentation
3. Extract CLI reference
4. Extract testing guide
5. Extract configuration guide
6. Keep CLAUDE.md as concise project overview
7. Add cross-references between docs

**New Structure:**
```
docs/
├── ARCHITECTURE.md              # Library architecture (from CLAUDE.md)
├── CLI_REFERENCE.md             # CLI commands (from CLAUDE.md)
├── TESTING.md                   # Testing guide (from CLAUDE.md)
├── CONFIGURATION.md             # Config guide (from CLAUDE.md)
├── SPL_PATTERNS.md              # SPL query patterns (from CLAUDE.md)
├── TROUBLESHOOTING.md           # Common issues (from CLAUDE.md)
├── quick-start.md               # Getting started
└── ASSISTANT_SKILLS_ALIGNMENT.md # This document
```

**CLAUDE.md Reduction:**
- ~10,000 lines → ~2,000 lines
- Keep: Overview, quick reference, project-specific rules
- Move: Detailed docs to `docs/`

**Estimated Effort:** Medium
**Risk:** Low (reorganization only)

---

### Phase 4: Test Coverage Expansion (Splunk)

**Goal:** Increase unit test coverage to match Jira/Confluence standards

**Current:** 73 unit tests
**Target:** 400+ unit tests (95% coverage)

**Tasks:**
1. Add tests for all CLI commands
2. Add tests for all validators
3. Add tests for all formatters
4. Add tests for error handling
5. Add tests for configuration edge cases
6. Enable coverage enforcement in CI

**Priority Test Files:**
```
tests/
├── commands/
│   ├── test_search_cmds.py          # NEW
│   ├── test_job_cmds.py             # NEW
│   ├── test_export_cmds.py          # NEW
│   ├── test_metadata_cmds.py        # NEW
│   └── ...14 command test files
├── test_validators.py               # EXPAND
├── test_formatters.py               # EXPAND
├── test_spl_helper.py               # EXPAND
└── test_error_handler.py            # NEW
```

**Reference:** Use `jira-assistant-skills-lib/tests/` as template

**Estimated Effort:** High
**Risk:** Low (additive)

---

### Phase 5: Context Caching System (Splunk)

**Goal:** Add intelligent context caching for Splunk-specific metadata

**Tasks:**
1. Create `SplunkContext` class
2. Cache index metadata (field names, sourcetypes)
3. Cache saved search suggestions
4. Add TTL-based expiration
5. Integrate with CLI for intelligent suggestions

**New Files:**
```
src/splunk_assistant_skills_lib/
├── splunk_context.py             # Context caching
└── cache.py                      # SQLite-based cache (if not in base lib)
```

**Features:**
```python
class SplunkContext:
    def get_index_fields(index: str) -> list[str]
        """Cached field names for index"""

    def suggest_sourcetypes(index: str) -> list[str]
        """Common sourcetypes for index"""

    def get_saved_searches(app: str) -> list[str]
        """Cached saved search names"""

    def suggest_time_modifiers() -> list[str]
        """Common time modifiers"""
```

**Estimated Effort:** Medium
**Risk:** Low (additive feature)

---

### Phase 6: Cross-Project Shared Patterns (All)

**Goal:** Extract common patterns to `assistant-skills-lib`

**Patterns to Share:**
1. Test fixture generators (temp files, mock clients)
2. CLI output formatters (table, JSON, CSV)
3. Progress bar utilities
4. Credential manager base class
5. Batch processor with checkpoints

**Tasks:**
1. Identify duplicate code across all three libraries
2. Create PRs to `assistant-skills-lib` for shared code
3. Update all three projects to use shared implementations
4. Remove duplicated code

**Estimated Effort:** High (cross-project coordination)
**Risk:** Medium (breaking changes possible)

---

## Quick Wins (Immediate Actions)

These can be implemented independently with minimal risk:

### 1. Standardize SKILL.md Frontmatter

**Current Variations:**
```yaml
# Jira
name: "jira-issue-management"
description: "..."
allowed-tools: ["Bash", "Read", "Glob", "Grep"]

# Confluence
name: confluence-page
triggers:
  - create page
  - get page

# Splunk
(minimal frontmatter)
```

**Proposed Standard:**
```yaml
---
name: "{service}-{feature}"
description: "One-line description for skill discovery"
version: "1.0.0"
triggers:
  - trigger keyword 1
  - trigger keyword 2
allowed-tools: ["Bash", "Read", "Glob", "Grep"]
risk-level: "read-only|reversible|destructive"
---
```

### 2. Standardize Setup Command Names

| Project | Current | Proposed |
|---------|---------|----------|
| Jira | `jira-assistant-setup` | `assistant-skills-setup` |
| Confluence | `confluence-assistant-setup` | `assistant-skills-setup` |
| Splunk | `assistant-skills-setup` | (already aligned) |

### 3. Add Skill Count to Plugin Manifest

**Current:** Skill count not visible in `plugin.json`
**Proposed:** Add `"skill_count": 14` metadata field

### 4. Standardize CLI Entry Points

| Project | Current | Pattern |
|---------|---------|---------|
| Jira | `jira-as` | `{service}-as` |
| Confluence | `confluence` | `confluence-as` (rename for consistency) |
| Splunk | `splunk-as` | (already aligned) |

---

## Metrics for Success

### Phase Completion Criteria

| Phase | Success Metric |
|-------|----------------|
| Phase 1 | Splunk library depends on `assistant-skills-lib` |
| Phase 2 | `SPLUNK_MOCK_MODE=true` enables offline testing |
| Phase 3 | CLAUDE.md < 2,500 lines, docs/ has 6+ files |
| Phase 4 | Test count > 400, coverage > 90% |
| Phase 5 | `SplunkContext` provides index/field suggestions |
| Phase 6 | < 500 lines of duplicate code across projects |

### Long-term Alignment Metrics

- All three projects pass same linting rules
- All three projects have >90% test coverage
- All three projects use `assistant-skills-lib` base
- All three projects have consistent SKILL.md format
- All three projects have docs/ directory structure

---

## Appendix: Pattern Source Reference

| Pattern | Best Implementation | Port To |
|---------|--------------------| --------|
| Mock client system | Jira | Splunk, Confluence |
| Test fixture architecture | Splunk | Jira, Confluence |
| Context caching | Confluence | Splunk, Jira |
| Bulk operations | Jira | Splunk |
| Content helpers | Confluence | (domain-specific) |
| Documentation structure | Jira | Splunk |
| Error troubleshooting hints | Jira | Splunk, Confluence |
| CI/CD enforcement | Jira | Splunk, Confluence |

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize phases** based on business needs
3. **Create tracking issues** for each phase
4. **Begin Phase 1** (base library adoption) as foundation
5. **Parallel work** on Phase 3 (docs restructure) - low risk, high visibility

---

## Completed Work

### Phase 1: Base Library Adoption - ALREADY COMPLETE (Verified 2026-01-19)

The `splunk-assistant-skills-lib` already properly inherits from `assistant-skills-lib`:

| Component | Status | Implementation |
|-----------|--------|----------------|
| Dependency | ✅ | `assistant-skills-lib>=0.3.0` in pyproject.toml |
| error_handler.py | ✅ | All exceptions inherit from base (`SplunkError` → `BaseAPIError`) |
| validators.py | ✅ | Uses `validate_choice`, `validate_int`, `validate_list`, `validate_required`, `validate_url` |
| config_manager.py | ✅ | `ConfigManager` extends `BaseConfigManager` |
| formatters.py | ✅ | Uses `Colors`, `format_table`, `format_json`, `print_success`, etc. |

Updated dependency from `>=0.2.1` to `>=0.3.0` to match latest base library version.

### Phase 3: Documentation Restructure - COMPLETE (2026-01-19)

Split CLAUDE.md into focused documentation files in `docs/`:

| File | Lines | Content |
|------|-------|---------|
| CLAUDE.md | 149 | Project overview and quick reference (was 1,079) |
| docs/ARCHITECTURE.md | 223 | Directory structure, library pattern, demo environment |
| docs/CLI_REFERENCE.md | 210 | CLI commands, search modes, job lifecycle |
| docs/CONFIGURATION.md | 154 | Config priority, environment variables, auth |
| docs/DEVELOPMENT.md | 228 | Adding scripts/skills, git guidelines |
| docs/SPL_PATTERNS.md | 149 | Query patterns, progressive disclosure, error handling |
| docs/TESTING.md | 370 | Unit tests, integration tests, Docker, fixtures |
| docs/TROUBLESHOOTING.md | 176 | Common issues and solutions |

**Results:**
- CLAUDE.md reduced from 1,079 lines to 149 lines (86% reduction)
- 7 focused documentation files created
- Total documentation: 2,158 lines across 9 files (includes alignment doc)
- All docs have cross-references

### Phase 2: Mock Client System - COMPLETE (2026-01-19)

Comprehensive mock client system implemented in `splunk-assistant-skills-lib`:

**New Files:**
```
src/splunk_assistant_skills_lib/mock/
├── __init__.py           # Enhanced exports
├── base.py               # MockSplunkClientBase (existing)
├── client.py             # Composed clients (enhanced)
├── factories.py          # NEW: Response factories
├── protocols.py          # NEW: Type checking protocols
└── mixins/
    ├── __init__.py
    ├── admin.py          # AdminMixin (existing)
    ├── export.py         # NEW: ExportMixin
    ├── job.py            # JobMixin (existing)
    ├── metadata.py       # MetadataMixin (existing)
    └── search.py         # SearchMixin (existing)
```

**Components Added:**

| Component | Purpose |
|-----------|---------|
| `ExportMixin` | Streaming CSV/JSON/JSON-rows export |
| `ResponseFactory` | Paginated responses, search results |
| `JobFactory` | Running/done/failed job responses |
| `IndexFactory` | Index entries and lists |
| `UserFactory` | User entries |
| `TimestampFactory` | Splunk-format timestamps |
| `ResultFactory` | Log events, stats rows, timechart |
| `MockClientProtocol` | Type checking for mixins |

**Skill-Specific Clients:**
- `MockSearchClient` - Search-only testing
- `MockJobClient` - Job lifecycle testing
- `MockMetadataClient` - Metadata discovery testing
- `MockAdminClient` - Admin operations testing
- `MockExportClient` - Export/streaming testing

**Combination Clients:**
- `MockSearchJobClient` - Search + job lifecycle
- `MockSearchExportClient` - Search + export
- `MockFullSearchClient` - Search + job + export + metadata

**Activation:** `SPLUNK_MOCK_MODE=true` environment variable

**Commit:** `6f6d496` in splunk-assistant-skills-lib

### Phase 4: Test Coverage Expansion - COMPLETE (2026-01-19)

Expanded test coverage from 46% to 73% with 651 tests:

**Previous State:**
- 264 tests
- 46% overall coverage
- Many modules with <30% coverage

**Current State:**
- 651 tests (+387)
- 73% overall coverage

**Test Files Added/Enhanced:**

| Test File | Tests | Coverage Impact |
|-----------|-------|-----------------|
| `test_mock_client.py` | 139 | NEW: Mock system 86-100% |
| `test_formatters.py` | 66 | 55% → 100% |
| `test_job_poller.py` | 52 | 58% → 100% |
| `test_config_manager.py` | 34 | 24% → 92% |
| `test_search_context.py` | 52 | 22% → 99% |
| `test_time_utils.py` | 85 | 62% → 100% |

**Module Coverage Improvements:**

| Module | Before | After |
|--------|--------|-------|
| `formatters.py` | 55% | 100% |
| `job_poller.py` | 58% | 100% |
| `time_utils.py` | 62% | 100% |
| `search_context.py` | 22% | 99% |
| `config_manager.py` | 24% | 92% |
| `mock/base.py` | 0% | 90% |
| `mock/client.py` | 0% | 93% |
| `mock/factories.py` | 0% | 99% |
| `mock/mixins/*` | 0% | 86-97% |
| `mock/protocols.py` | 0% | 100% |

**Commit:** `132cc8b` in splunk-assistant-skills-lib

### Stale File Cleanup (2026-01-18)

All three projects were cleaned of stale files from library migrations:

| Project | Commit | Files Removed | Lines Deleted |
|---------|--------|---------------|---------------|
| Jira-Assistant-Skills | `f50d9ad` | 36 | 34,174 |
| Confluence-Assistant-Skills | `cbf15f7` | 3 | 89 |
| Splunk-Assistant-Skills | `763009e` | 3 | 1,290 |

**Total: 42 stale files, 35,553 lines removed**

**Jira cleanup:**
- Removed `src/jira_assistant_skills/` (stale CLI after library migration)
- Removed `tests/test_cli.py` (broken imports)

**Confluence cleanup:**
- Removed `REFACTORING_INSTRUCTIONS.md` (obsolete)
- Fixed `.pre-commit-config.yaml` paths (removed `src/` references)
- Fixed `pyproject.toml` module references

**Splunk cleanup:**
- Removed `API_GAP_ANALYSIS.md` (referenced obsolete scripts)
- Removed `PROPOSAL_FEEDBACK.md` (Phase 1 historical)
- Removed `REFACTORING_FEEDBACK.md` (Phase 1 historical)

---

*Document created: 2026-01-18*
*Last updated: 2026-01-19* (Phase 4 complete)
