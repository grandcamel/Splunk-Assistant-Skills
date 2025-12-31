# Refactoring Proposal: Centralizing Assistant-Skills Libraries and Scripts

**Author:** Gemini AI Agent
**Date:** December 30, 2025
**Status:** DRAFT
**Reviewer:** Claude (Opus 4.5)
**Review Date:** December 31, 2025

---

## 1. Abstract

The `Assistant-Skills` ecosystem currently comprises several projects, each with its own Python library (`...-lib`). This has led to significant code duplication, particularly for common functionalities like configuration management, error handling, and input validation. Furthermore, the skill execution model relies on invoking Python scripts via their full file path, creating a brittle coupling to the filesystem layout.

This proposal outlines a two-phase refactoring plan to address these issues.
*   **Phase 1** will consolidate all duplicated, non-domain-specific code from the `jira-`, `confluence-`, and `splunk-assistant-skills-lib` projects into the central `assistant-skills-lib`.
*   **Phase 2** will transform the skill scripts into formal command-line entry points distributed by their respective Python packages, decoupling skill execution from the file system.

This effort will drastically reduce code duplication, improve long-term maintainability, and align the projects with standard Python packaging and distribution practices.

> **REVIEW NOTE:** The abstract accurately describes Phase 1's goals. However, Phase 2's problem statement requires validation - see Section 2 feedback.

---

## 2. Background & Problem Statement

The `Assistant-Skills` architecture is a "factory" model where the `Assistant-Skills` project provides templates and tools to create service-specific plugins (e.g., `Jira-Assistant-Skills`). While this has successfully standardized the project structure, it has led to two significant technical debts.

### Problem A: Systemic Code Duplication Across Libraries

The service-specific libraries (`confluence-lib`, `jira-lib`, `splunk-lib`) were developed independently and contain large amounts of functionally identical boilerplate code.

**Evidence of Duplication:**

| Common Module | `assistant-skills-lib` | `confluence-lib` | `jira-lib` | `splunk-lib` |
| :--- | :---: | :---: | :---: | :---: |
| `error_handler.py` | Yes | Yes | Yes | Yes |
| `formatters.py` | Yes | Yes | Yes | Yes |
| `validators.py` | Yes | Yes | Yes | Yes |
| `config_manager.py`| No | Yes | Yes | Yes |

This duplication means that:
*   Fixing a bug in the error handling logic for Jira requires manually porting the fix to Confluence and Splunk.
*   The overall maintenance burden is 3x higher than it needs to be for common code.
*   There is a high risk of divergence, where subtle differences can emerge over time, leading to inconsistent behavior across the different `Assistant-Skills` projects.

> **REVIEW: VALIDATED** - Problem A is well-documented and the evidence table is accurate. This is a genuine maintenance burden.

### Problem B: Brittle Filesystem-Coupled Skill Execution

Currently, `SKILL.md` files trigger functionality by invoking a Python script directly via its path:
```bash
# Example from a current SKILL.md
python .claude/skills/jira-issue/scripts/get_issue.py PROJ-123
```
This approach is problematic because:
*   It is tightly coupled to the project's directory structure.
*   It is not a standard or professional way to distribute and execute code within a Python package.
*   It makes the scripts less portable and harder to test or execute outside the specific context of the Claude Code runner.

> **REVIEW: REQUIRES VALIDATION**
>
> Analysis of the actual `Splunk-Assistant-Skills` codebase reveals a **different pattern** than described:
>
> ```bash
> # From skills/splunk-search/SKILL.md (actual content)
> python search_oneshot.py "index=main | stats count by sourcetype"
> python search_oneshot.py "index=main | head 100" --earliest -1h --latest now
> python search_oneshot.py "index=main | top host" --output json
> ```
>
> The Splunk SKILL.md files use **relative paths**, not full filesystem paths. This suggests:
> 1. Claude Code may set the working directory to the scripts folder before execution
> 2. The brittleness claim may be overstated for this project
> 3. Different Assistant-Skills projects may use different patterns
>
> **Action Required:** Before proceeding with Phase 2, conduct a survey across all three projects (Jira, Confluence, Splunk) to document the actual invocation patterns. The Phase 2 value proposition depends on this finding.

---

## 3. Proposed Solution

This refactoring will be executed in two distinct phases.

### Phase 1: Library Consolidation & Centralization

**Goal:** Establish the base `assistant-skills-lib` as the single source of truth for all common, non-domain-specific code.

**Detailed Steps:**

1.  **Enhance `assistant-skills-lib`:**
    *   A new, generic `BaseConfigManager` will be created in the base library. It will handle the universal logic of finding the `.claude` directory, loading and merging `settings.json` and `settings.local.json`, and managing profiles.
    *   The existing `error_handler.py`, `validators.py`, and `formatters.py` modules in the base library will be reviewed and updated to become the canonical versions.

2.  **Refactor Service-Specific Libraries:**
    *   The `ConfigManager` within each service library (`jira-`, `confluence-`, etc.) will be refactored to inherit from the new `BaseConfigManager`. It will only retain service-specific logic (e.g., `get_agile_fields` in the Jira lib).
    *   The duplicated `error_handler.py`, `validators.py`, and `formatters.py` files will be **deleted** from the service-specific libraries.
    *   Imports within the service-specific libraries will be updated to reference the base `assistant-skills-lib` (e.g., `from assistant_skills_lib.error_handler import handle_errors`).

3.  **Update Dependencies:**
    *   The `pyproject.toml` for `confluence-`, `jira-`, and `splunk-assistant-skills-lib` will be modified to declare a formal dependency on `assistant-skills-lib`.

> **REVIEW: MISSING SPECIFICATION**
>
> The `BaseConfigManager` design needs to be specified before implementation. Proposed interface:
>
> ```python
> from abc import ABC, abstractmethod
> from typing import Any, Optional
> from pathlib import Path
>
> class BaseConfigManager(ABC):
>     """Base configuration manager for Assistant-Skills projects."""
>
>     # Concrete methods (shared across all services)
>     def find_claude_directory(self) -> Optional[Path]:
>         """Locate the .claude directory in project hierarchy."""
>         ...
>
>     def load_settings(self) -> dict[str, Any]:
>         """Load and merge settings.json and settings.local.json."""
>         ...
>
>     def get_profile(self, name: Optional[str] = None) -> dict[str, Any]:
>         """Get a named profile or the default profile."""
>         ...
>
>     def get_env_override(self, key: str) -> Optional[str]:
>         """Check for environment variable override."""
>         ...
>
>     # Abstract methods (service-specific)
>     @abstractmethod
>     def get_service_name(self) -> str:
>         """Return service name (e.g., 'splunk', 'jira')."""
>         ...
>
>     @abstractmethod
>     def get_default_config(self) -> dict[str, Any]:
>         """Return service-specific default configuration."""
>         ...
>
>     @abstractmethod
>     def validate_profile(self, profile: dict[str, Any]) -> None:
>         """Validate service-specific profile requirements."""
>         ...
> ```
>
> **Gap: Service-Specific Validators**
>
> The proposal does not address validators that are inherently service-specific:
>
> | Service | Service-Specific Validators |
> |---------|----------------------------|
> | Splunk | `validate_spl()`, `validate_sid()`, `validate_time_modifier()` |
> | Jira | `validate_issue_key()`, `validate_jql()` |
> | Confluence | `validate_page_id()`, `validate_space_key()` |
>
> **Recommendation:** These validators should remain in their respective service libraries. Only generic validators (e.g., `validate_non_empty_string()`, `validate_positive_int()`) should move to the base library.

### Phase 2: Script-to-Entry-Point Refactoring

**Goal:** Decouple skill execution from the filesystem by converting skill scripts into standard Python package command-line entry points. This phase will be piloted with the `Jira-Assistant-Skills` project first.

**Detailed Steps:**

1.  **Move Scripts:** The Python script files will be moved from their current location (e.g., `Jira-Assistant-Skills/.claude/skills/jira-issue/scripts/get_issue.py`) into the library's source tree (e.g., `Jira-Assistant-Skills/jira-assistant-skills-lib/src/jira_assistant_skills_lib/scripts/get_issue.py`).

2.  **Define Entry Points:** The `pyproject.toml` of the service-specific library will be updated to include a `[project.scripts]` table. This automatically creates command-line executables upon package installation.

    **Example `pyproject.toml` modification:**
    ```toml
    [project.scripts]
    jira-get-issue = "jira_assistant_skills_lib.scripts.get_issue:main"
    jira-create-issue = "jira_assistant_skills_lib.scripts.create_issue:main"
    # ... and so on for all other scripts
    ```

3.  **Update `SKILL.md` Files:** The `bash` command blocks within all `SKILL.md` files will be updated to use the new, clean entry point commands.

    **Before:**
    ```bash
    python .claude/skills/jira-issue/scripts/get_issue.py PROJ-123 --output json
    ```
    **After:**
    ```bash
    jira-get-issue PROJ-123 --output json
    ```

> **REVIEW: SIGNIFICANT CONCERNS**
>
> **Concern 1: Global Namespace Pollution**
>
> Across all three projects, there are approximately 80+ scripts each, totaling 240+ global CLI commands:
>
> | Project | Script Count | Example Entry Points |
> |---------|--------------|---------------------|
> | Splunk | 83 | `splunk-search-oneshot`, `splunk-create-job`, `splunk-list-indexes`... |
> | Jira | ~80 (est.) | `jira-get-issue`, `jira-create-issue`, `jira-search`... |
> | Confluence | ~60 (est.) | `confluence-get-page`, `confluence-create-page`... |
>
> Problems with 200+ global commands:
> - Shell tab-completion becomes unusable
> - Potential collision with existing system tools (e.g., `splunk` CLI already exists)
> - Discovery problem: users cannot easily list available commands
> - Global PATH pollution
>
> **Alternative Approaches:**
>
> | Approach | Example | Pros | Cons |
> |----------|---------|------|------|
> | Current proposal | `jira-get-issue` | Standard Python, discoverable via `which` | Namespace pollution |
> | Dispatcher pattern | `jas issue get PROJ-123` | Single entry point, subcommands | More complex implementation |
> | Abbreviated namespace | `jas-get-issue` | Shorter names | Less discoverable |
> | Local bin directory | `./bin/get_issue.py` | No global installation | Requires PATH setup |
>
> **Recommendation:** Consider the dispatcher pattern with a single entry point per service:
> ```bash
> splunk-skills search oneshot "index=main | head 10"
> jira-skills issue get PROJ-123
> confluence-skills page get 12345
> ```
>
> **Concern 2: Test Refactoring Impact**
>
> The current test pattern mocks at the script module level:
>
> ```python
> # Current test pattern (skills/splunk-app/tests/test_app_operations.py)
> @patch("list_apps.get_splunk_client")
> @patch("list_apps.format_table")
> def test_list_apps_text_output(self, mock_format, mock_get_client, mock_splunk_client):
>     mock_get_client.return_value = mock_splunk_client
>     from list_apps import main
>     main()
> ```
>
> After moving scripts into the library:
>
> ```python
> # New test pattern required (all mock paths change)
> @patch("splunk_assistant_skills_lib.scripts.list_apps.get_splunk_client")
> @patch("splunk_assistant_skills_lib.scripts.list_apps.format_table")
> def test_list_apps_text_output(self, mock_format, mock_get_client, mock_splunk_client):
>     mock_get_client.return_value = mock_splunk_client
>     from splunk_assistant_skills_lib.scripts.list_apps import main
>     main()
> ```
>
> **Impact Assessment (Splunk only):**
> - ~335 total tests
> - Estimated 70%+ require mock path updates
> - Every `@patch()` decorator needs review
> - Test discovery paths change
>
> This is not just "running tests to validate" - it is substantial test refactoring that should be planned explicitly.

---

## 4. Benefits

*   **Drastically Reduced Maintenance:** A bug fix in `error_handler.py` is made in one place and instantly benefits all three service projects.
*   **Code Simplification:** The service-specific libraries will become significantly smaller and focused only on their core domain logic.
*   **Improved Robustness & Consistency:** All projects will share the exact same implementation for configuration, validation, and error handling.
*   **Professional Packaging:** Adopts the standard, modern Python practice for distributing command-line tools, making the projects easier to understand, install, and use.
*   **Future-Proofing:** Establishes a clean, DRY (Don't Repeat Yourself) architecture that makes it trivial to create new, high-quality `*-Assistant-Skills` projects in the future.

> **REVIEW: ADDITIONAL CONSIDERATIONS**
>
> The benefits are accurate but should be weighed against costs:
>
> | Benefit | Counter-Consideration |
> |---------|----------------------|
> | Single bug fix location | Introduces single point of failure for all projects |
> | Smaller service libraries | Adds dependency management complexity |
> | Consistent behavior | Removes flexibility for service-specific customization |
> | Professional packaging | Increases installation complexity for end users |
>
> **Net Assessment:** Phase 1 benefits likely outweigh costs. Phase 2 benefits are less clear until the problem statement is validated.

---

## 5. Risks & Mitigation Strategy

*   **Risk:** The scale of the refactoring could introduce regressions.
    *   **Mitigation:** The phased approach isolates changes. The project's extensive test suites are the primary defense. No change will be considered complete until all unit, integration (`live_integration`), and end-to-end (`e2e`) tests are passing.

*   **Risk:** Modifying imports across hundreds of files is potentially error-prone.
    *   **Mitigation:** Changes will be performed using IDE tooling and `grep`/`sed` for batch replacements, followed by validation via static analysis (`mypy`) and the test suites.

> **REVIEW: ADDITIONAL RISKS IDENTIFIED**
>
> ### Risk 3: Version Dependency Chain (HIGH)
>
> The proposal creates a deep dependency chain:
>
> ```
> assistant-skills-lib (base)
>     ^
>     |-- jira-assistant-skills-lib
>     |-- confluence-assistant-skills-lib
>     +-- splunk-assistant-skills-lib
> ```
>
> **Problems:**
> 1. When `assistant-skills-lib` releases a breaking change, all downstream libs must update simultaneously
> 2. Version pinning becomes complex: `splunk-lib>=0.3.0` requires `assistant-lib>=1.2.0,<2.0.0`
> 3. Release coordination overhead increases
> 4. A bug in base lib affects all three projects simultaneously
>
> **Mitigation Required:**
> - Define semantic versioning policy for base library
> - Document version compatibility matrix
> - Consider using version ranges with upper bounds: `assistant-skills-lib>=1.0.0,<2.0.0`
> - Establish release coordination process
>
> ### Risk 4: Missing Migration Path (MEDIUM)
>
> The proposal does not address:
> - Users with existing installations
> - Backward compatibility during transition
> - Upgrade documentation
>
> **Mitigation Required:**
> - Document upgrade path for each phase
> - Consider deprecation warnings before removing old patterns
> - Provide migration scripts if configuration schema changes
>
> ### Risk 5: Entry Point Naming Collisions (MEDIUM)
>
> Global CLI commands may conflict with existing tools:
> - `splunk` command already exists (Splunk CLI)
> - `jira` command may exist (other Jira CLI tools)
>
> **Mitigation Required:**
> - Research existing CLI tool names before finalizing entry point names
> - Consider prefixes: `as-splunk-search` (assistant-skills-splunk-search)
> - Or use dispatcher pattern to minimize global commands
>
> ### Risk 6: No Rollback Plan (MEDIUM)
>
> If Phase 1 or Phase 2 introduces critical bugs in production:
> - How do users rollback to pre-refactor versions?
> - Are old package versions preserved on PyPI?
> - What is the escape hatch?
>
> **Mitigation Required:**
> - Ensure all pre-refactor versions remain available on PyPI
> - Document rollback procedure: `pip install splunk-assistant-skills-lib==0.2.2`
> - Consider feature flags for gradual rollout

---

## 6. Testing & Validation

The existing test suites are critical to the success of this refactoring.
1.  **Phase 1 Validation:** After centralizing the library code and refactoring `jira-assistant-skills-lib`, the full test suite for the `Jira-Assistant-Skills` project will be executed. The process will be repeated for Confluence and Splunk. This ensures the core logic remains sound.
2.  **Phase 2 Validation:** After converting the Jira scripts to entry points, the End-to-End test suite (`run-e2e-tests.sh`) will be executed. This is the ultimate validation, as it simulates the Claude Code environment executing the modified `SKILL.md` commands.

> **REVIEW: TEST PLAN ENHANCEMENT NEEDED**
>
> The current test plan underestimates the work required. Recommended additions:
>
> ### Pre-Refactoring Baseline
>
> Before any changes:
> 1. Run full test suite and record pass/fail counts
> 2. Generate test coverage report as baseline
> 3. Document any flaky tests
>
> ### Phase 1 Test Plan
>
> | Step | Action | Success Criteria |
> |------|--------|------------------|
> | 1a | Centralize `error_handler.py` | All tests pass, no import errors |
> | 1b | Centralize `validators.py` | All tests pass |
> | 1c | Centralize `formatters.py` | All tests pass |
> | 1d | Introduce `BaseConfigManager` | All tests pass, config behavior unchanged |
> | 1e | Update downstream libs | All three projects' tests pass |
>
> Each step should have a 1-week soak period in a staging/beta release before proceeding.
>
> ### Phase 2 Test Plan
>
> | Step | Action | Success Criteria |
> |------|--------|------------------|
> | 2a | Audit test mock paths | Document all `@patch()` decorators that will change |
> | 2b | Move scripts to library | Unit tests pass (with updated paths) |
> | 2c | Add entry points | Entry points callable from shell |
> | 2d | Update SKILL.md files | E2E tests pass |
> | 2e | Remove old script locations | No remaining references to old paths |
>
> ### Test Migration Estimate (Splunk)
>
> ```
> Total tests: 335
> Tests with @patch decorators: ~200 (estimated)
> Tests requiring path updates: ~140 (70%)
> Estimated refactoring time: 2-4 hours for Splunk alone
> ```
>
> ### Shared Test Infrastructure Gap
>
> The proposal does not address shared test utilities:
>
> ```
> skills/shared/tests/live_integration/
> ├── fixtures.py          # Reusable test fixtures
> ├── splunk_container.py  # Docker Splunk container management
> ├── test_utils.py        # Test helper functions
> ```
>
> **Question:** Should test utilities be centralized in `assistant-skills-lib`? Different services need different test infrastructure (Splunk Docker container vs Jira Cloud mock server).
>
> **Recommendation:** Keep test utilities in service-specific projects. Only truly generic test utilities (e.g., `assert_json_structure()`) should move to base library.

---

## 7. Request for Feedback

This proposal is open for review. Feedback on the following points would be particularly valuable:
1.  Are there any unforeseen risks or dependencies this plan overlooks?
2.  Should this refactoring be expanded to include other duplicated modules that may have been missed?
3.  Are there any team preferences regarding the naming conventions for the new command-line entry points (e.g., `jira-get-issue` vs. `jas-get-issue`)?

> **REVIEW RESPONSES:**
>
> **Q1: Unforeseen risks?**
>
> Yes, several identified above:
> - Version dependency chain management
> - Test refactoring underestimated
> - Entry point namespace pollution
> - Missing migration path
> - No rollback plan
> - Phase 2 problem statement may be inaccurate
>
> **Q2: Other duplicated modules?**
>
> Potential candidates for centralization not mentioned:
> - HTTP client base class (if patterns are similar across services)
> - Output formatting utilities (`print_success`, `print_error`, `print_warning`)
> - Argument parsing helpers (common `argparse` patterns)
> - Logging configuration
>
> However, recommend caution: only centralize code that is **truly identical** across services. Service-specific variations should remain local.
>
> **Q3: Naming conventions?**
>
> Recommendations in order of preference:
>
> | Option | Pattern | Example | Rationale |
> |--------|---------|---------|-----------|
> | 1 (Recommended) | Dispatcher | `splunk-skills search oneshot "..."` | Single entry point, hierarchical, discoverable |
> | 2 | Abbreviated prefix | `sas-search-oneshot` | Short, avoids collision with `splunk` command |
> | 3 | Full prefix | `splunk-assistant-search-oneshot` | Unambiguous but verbose |
> | 4 (Proposed) | Simple prefix | `splunk-search-oneshot` | May conflict with `splunk` CLI |

---

## 8. Revised Implementation Roadmap

Based on review feedback, the following phased approach is recommended:

### Pre-Phase: Validation & Planning (1-2 weeks)

- [ ] Survey all three projects for actual SKILL.md invocation patterns
- [ ] Validate Phase 2 problem statement
- [ ] Define `BaseConfigManager` interface specification
- [ ] Document version compatibility strategy
- [ ] Create test migration plan with effort estimates
- [ ] Decide on entry point naming convention
- [ ] Document rollback procedures

### Phase 1a: Error Handler Centralization (1 week)

- [ ] Move `error_handler.py` to `assistant-skills-lib`
- [ ] Update imports in all three downstream libs
- [ ] Run full test suites
- [ ] Release as minor version bump
- [ ] 1-week soak period

### Phase 1b: Validators Centralization (1 week)

- [ ] Move generic validators to `assistant-skills-lib`
- [ ] Keep service-specific validators in service libs
- [ ] Update imports
- [ ] Run full test suites
- [ ] Release as minor version bump
- [ ] 1-week soak period

### Phase 1c: Formatters Centralization (1 week)

- [ ] Move `formatters.py` to `assistant-skills-lib`
- [ ] Update imports
- [ ] Run full test suites
- [ ] Release as minor version bump
- [ ] 1-week soak period

### Phase 1d: BaseConfigManager Introduction (2 weeks)

- [ ] Implement `BaseConfigManager` in `assistant-skills-lib`
- [ ] Refactor `SplunkConfigManager` to inherit from base
- [ ] Refactor `JiraConfigManager` to inherit from base
- [ ] Refactor `ConfluenceConfigManager` to inherit from base
- [ ] Run full test suites
- [ ] Release as minor version bump
- [ ] 2-week soak period

### Phase 2: Entry Points (Conditional)

**Proceed only if Pre-Phase validation confirms the problem statement.**

- [ ] Pilot with Jira project only
- [ ] Refactor tests to use new module paths
- [ ] Move scripts into library
- [ ] Define entry points in `pyproject.toml`
- [ ] Update SKILL.md files
- [ ] Run E2E tests
- [ ] Evaluate results before expanding to other projects

---

## 9. Decision Log

| Date | Decision | Rationale | Owner |
|------|----------|-----------|-------|
| 2025-12-30 | Proposal drafted | Initial proposal | Gemini |
| 2025-12-31 | Risk review completed | Identified gaps and risks | Claude |
| TBD | Phase 2 validation | Confirm problem statement | TBD |
| TBD | Naming convention selected | Team consensus | TBD |
| TBD | `BaseConfigManager` interface approved | Design review | TBD |

---

## Appendix A: Current Splunk Architecture Reference

For context, the current Splunk-Assistant-Skills architecture:

```
Splunk-Assistant-Skills/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── .claude/
│   ├── settings.example.json    # Example config
│   └── settings.local.json      # Personal credentials (gitignored)
├── skills/
│   ├── splunk-assistant/        # Hub router (14 total skills)
│   ├── splunk-search/           # 6 scripts
│   ├── splunk-job/              # 10 scripts
│   ├── ... (11 more skills)
│   └── shared/
│       ├── config/
│       │   └── config.schema.json
│       └── tests/
│           └── live_integration/
├── conftest.py                  # Root pytest fixtures
├── pytest.ini                   # Test configuration
├── requirements.txt             # Dependencies (includes splunk-assistant-skills-lib>=0.2.2)
└── pyproject.toml               # Tool configuration (black, isort)
```

**Key Statistics:**
- 14 skills
- 83 Python scripts
- 335 tests (160 unit, 175 live integration)
- All scripts import from PyPI package `splunk-assistant-skills-lib`

---

## Appendix B: Version Compatibility Matrix Template

To be completed during Pre-Phase:

```
assistant-skills-lib
├── v1.0.x (current)
│   ├── splunk-assistant-skills-lib: v0.2.x - v0.3.x
│   ├── jira-assistant-skills-lib: v0.x.x - v0.x.x
│   └── confluence-assistant-skills-lib: v0.x.x - v0.x.x
│
├── v1.1.x (Phase 1a-1c)
│   ├── splunk-assistant-skills-lib: v0.3.x+
│   ├── jira-assistant-skills-lib: v0.x.x+
│   └── confluence-assistant-skills-lib: v0.x.x+
│
└── v2.0.x (Phase 1d - breaking changes)
    ├── splunk-assistant-skills-lib: v1.0.x+
    ├── jira-assistant-skills-lib: v1.0.x+
    └── confluence-assistant-skills-lib: v1.0.x+
```
