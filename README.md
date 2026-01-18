<p align="center">
  <img src="assets/logo.svg" alt="Splunk Assistant Skills" width="140">
</p>

<h1 align="center">Splunk Assistant Skills</h1>

<table align="center">
<tr>
<td align="center">
<h2>80%</h2>
<sub>Faster than manual<br>SPL workflows</sub>
</td>
<td align="center">
<h2>14</h2>
<sub>Specialized skills<br>one conversation</sub>
</td>
<td align="center">
<h2>83</h2>
<sub>Production-ready<br>Python scripts</sub>
</td>
<td align="center">
<h2>0</h2>
<sub>SPL syntax<br>to memorize</sub>
</td>
</tr>
</table>

<p align="center">
  <img src="https://img.shields.io/badge/tests-348%20passing%2C%207%20xfail-brightgreen?logo=pytest" alt="Tests">
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/skills-14-FF6900" alt="Skills">
  <a href="https://pypi.org/project/splunk-assistant-skills-lib/"><img src="https://img.shields.io/pypi/v/splunk-assistant-skills-lib?color=blue&logo=pypi&logoColor=white" alt="PyPI"></a>
  <img src="https://img.shields.io/github/stars/grandcamel/Splunk-Assistant-Skills?style=social" alt="GitHub Stars">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
</p>

<p align="center">
  <strong>Talk to Splunk like a colleague, not a query language.</strong><br>
  <sub>Natural language search, job management, and administration for Splunk via Claude Code.</sub>
</p>

<div align="center">

```
> "Show me error patterns in the main index from the last hour"

Claude: Running SPL query...
  index=main error earliest=-1h | stats count by host, sourcetype | sort -count

Found 847 errors across 12 hosts. Top sources:
  web-prod-01  nginx:error     423
  api-srv-03   application     298
  db-master    postgresql      126
```

</div>

<p align="center">
  <a href="#quick-start"><strong>Get Started</strong></a> &bull;
  <a href="#skills-overview">Skills</a> &bull;
  <a href="#who-is-this-for">Use Cases</a> &bull;
  <a href="#architecture">Architecture</a>
</p>

---

## The Difference

<table>
<tr>
<td width="50%">

### The SPL Way
```spl
index=main sourcetype=access_combined
| eval response_time=response_time/1000
| where response_time > 2
| stats avg(response_time) as avg_rt,
        max(response_time) as max_rt,
        count by host
| sort -count
| head 10
```
*Hope you remembered the syntax...*

</td>
<td width="50%">

### The Natural Way
```
"Show me slow API responses over 2 seconds,
 grouped by host, top 10"
```
*Just ask.*

</td>
</tr>
</table>

### Time Saved

| Task | Traditional Splunk | Splunk Assistant | Saved |
|------|------------------|----------------|-------|
| Write complex SPL query | 5-15 min | 30 sec | 90% |
| Check job status & results | 2-3 min | 10 sec | 95% |
| Export large dataset | 5-10 min | 1 min | 85% |
| Create saved search | 3-5 min | 30 sec | 90% |
| Debug search errors | 5-20 min | 1 min | 80% |

**Typical user:** Save 3-5 hours per week.

---

## Quick Start

### Option A: Install as Claude Code Plugin (Recommended)

```bash
# Install from GitHub
claude plugin add github:grandcamel/Splunk-Assistant-Skills
```

### Option B: Manual Installation

#### 1. Clone and Install Dependencies

```bash
git clone https://github.com/grandcamel/Splunk-Assistant-Skills.git
cd Splunk-Assistant-Skills
pip install -r requirements.txt
```

#### 2. Get API Token

1. Log into Splunk Web
2. Go to **Settings > Tokens**
3. Click **New Token**, select your user
4. Copy the generated token

#### 3. Configure

```bash
# Set environment variables
export SPLUNK_TOKEN="your-jwt-token"
export SPLUNK_SITE_URL="https://splunk.example.com"

# Or create .claude/settings.local.json for profiles
```

#### 4. Install CLI

```bash
# Install the splunk-as CLI
pip install splunk-assistant-skills-lib

# Verify installation
splunk-as --version
```

#### 5. Start Using

```bash
# CLI usage (recommended)
splunk-as search oneshot "index=main | stats count by sourcetype" --earliest -1h

# Or with Claude Code
> "Search for errors in the main index from the last hour"
```

**That's it.** Claude now has full Splunk access.

<p align="center">
  <a href="CLAUDE.md"><strong>Full Setup Guide</strong></a>
</p>

---

## Setup (Assistant Skills)

If you installed via the plugin system, run the setup wizard:

```bash
/assistant-skills-setup
```

This configures:
- Shared Python venv at `~/.assistant-skills-venv/`
- Required dependencies from `requirements.txt`
- Environment variables (prompts you to set credentials)
- `claude-as` shell function for running Claude with dependencies

After setup, use `claude-as` instead of `claude`:
```bash
claude-as  # Runs Claude with Assistant Skills venv activated
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SPLUNK_SITE_URL` | Yes | Splunk server URL (e.g., `https://splunk.example.com`) |
| `SPLUNK_TOKEN` | Auth* | Bearer token (preferred). Create in Splunk Web: Settings > Tokens |
| `SPLUNK_USERNAME` | Auth* | Basic auth username (alternative to token) |
| `SPLUNK_PASSWORD` | Auth* | Basic auth password (use with `SPLUNK_USERNAME`) |
| `SPLUNK_MANAGEMENT_PORT` | No | Management API port (default: `8089`) |
| `SPLUNK_VERIFY_SSL` | No | Verify SSL certificates (default: `true`) |
| `SPLUNK_DEFAULT_APP` | No | Default Splunk app context (default: `search`) |
| `SPLUNK_DEFAULT_INDEX` | No | Default search index (default: `main`) |

*\*Authentication: Either `SPLUNK_TOKEN` OR both `SPLUNK_USERNAME` and `SPLUNK_PASSWORD` required.*

---

## What You Can Do

```mermaid
flowchart LR
    subgraph Input["You Say"]
        A["Search for errors"]
        B["Export yesterday's logs"]
        C["Show my saved searches"]
        D["Create an alert"]
    end

    subgraph Processing["Claude Understands"]
        E["splunk-search"]
        F["splunk-export"]
        G["splunk-savedsearch"]
        H["splunk-alert"]
    end

    subgraph Output["You Get"]
        I["Formatted results"]
        J["CSV/JSON file"]
        K["Search list"]
        L["Alert configured"]
    end

    A --> E --> I
    B --> F --> J
    C --> G --> K
    D --> H --> L
```

<details>
<summary><strong>Example: Security Analyst's Morning</strong></summary>

**Before Splunk Assistant (45 minutes)**
1. Open Splunk Web, navigate to search
2. Write SPL for failed logins: `index=security action=failure | stats count by user, src_ip | sort -count`
3. Copy results, open spreadsheet
4. Write another query for privilege escalation
5. Cross-reference with yesterday's baseline
6. Document findings in ticket

**After Splunk Assistant (5 minutes)**
> Analyst: "Show me failed logins in the last 24 hours, group by user and source IP, compare to yesterday's baseline, and flag any anomalies"

Claude provides a formatted summary with highlighted anomalies.

**Time saved:** 40 minutes every morning

</details>

---

## Skills Overview

| Skill | Purpose | Example Command |
|-------|---------|-----------------|
| `splunk-assistant` | Hub router with progressive disclosure | "Help me search Splunk" |
| `splunk-search` | SPL query execution (oneshot/normal/blocking) | "Search for 404 errors in nginx logs" |
| `splunk-job` | Search job lifecycle management | "Check status of job abc123" |
| `splunk-export` | High-volume streaming extraction | "Export last week's firewall logs to CSV" |
| `splunk-metadata` | Index, source, sourcetype discovery | "List all available indexes" |
| `splunk-lookup` | CSV and lookup file management | "Upload users.csv as a lookup" |
| `splunk-tag` | Knowledge object tagging | "Tag host web-01 as production" |
| `splunk-savedsearch` | Reports and scheduled searches | "Show my saved searches" |
| `splunk-alert` | Alert triggering and monitoring | "Create alert for high error rate" |
| `splunk-rest-admin` | REST API configuration access | "Get server info" |
| `splunk-security` | Token management and RBAC | "List authentication tokens" |
| `splunk-metrics` | Real-time metrics (mstats, mcatalog) | "Show CPU metrics by host" |
| `splunk-app` | Application management | "List installed apps" |
| `splunk-kvstore` | App Key Value Store operations | "Query the threat intel collection" |

<p align="center">
  <a href="CLAUDE.md"><strong>Full Scripts Reference</strong></a>
</p>

---

## Who Is This For?

<details>
<summary><strong>Developers</strong> — Never leave your terminal</summary>

**Stop context-switching to Splunk Web.**

You're debugging in your IDE. You need to check logs. Stay in your terminal.

```bash
claude "Show me errors from my-app in the last hour"
# Done in 3 seconds, never left your terminal
```

### Developer Cheat Sheet

| Task | Command |
|------|---------|
| Search logs | "Search for errors in app-name last hour" |
| Check deployments | "Find deployment events today" |
| Debug issues | "Show stack traces from main index" |
| Export for analysis | "Export last 1000 errors to JSON" |

**Time saved:** ~45 min/week

</details>

<details>
<summary><strong>Security Analysts</strong> — Investigate faster</summary>

**Accelerate threat hunting and incident response.**

### Quick Investigations
```
"Find all failed SSH attempts in the last 24 hours"
"Show authentication events for user john.doe"
"Search for privilege escalation patterns"
```

### Common Operations

| Task | Command |
|------|---------|
| Failed logins | "Show failed logins by user and IP" |
| Suspicious activity | "Find unusual outbound connections" |
| Threat hunting | "Search for indicators: 192.168.1.100, malware.exe" |
| Incident timeline | "Build timeline for host web-01 last 4 hours" |

**Time saved:** Minutes per investigation

</details>

<details>
<summary><strong>IT Operations</strong> — Monitor and respond</summary>

**Real-time visibility without the query complexity.**

### Quick Actions
```
"Show critical alerts from last 24 hours"
"Check system health across all hosts"
"Find hosts with high CPU usage"
```

### Common Operations

| Task | Command |
|------|---------|
| Alert review | "Show triggered alerts today" |
| Performance | "CPU and memory stats by host" |
| Capacity | "Disk usage trends this week" |
| Incidents | "Errors across production hosts" |

**Time saved:** Hours per week on routine checks

</details>

<details>
<summary><strong>Data Engineers</strong> — ETL without the complexity</summary>

**Extract data at scale with simple commands.**

### Data Extraction
```
"Export last week's firewall logs to CSV"
"Stream authentication events to JSON file"
"Download metrics data for analysis"
```

### Common Operations

| Task | Command |
|------|---------|
| Bulk export | "Export index=main last 7 days to CSV" |
| Filtered extract | "Export errors from web tier to JSON" |
| Metrics dump | "Download CPU metrics for all hosts" |
| Schema discovery | "Show all fields in sourcetype=nginx" |

**Time saved:** Hours per data pipeline

</details>

---

## Architecture

```mermaid
flowchart TD
    U["User Request"] --> CC["Claude Code"]
    CC --> HA["splunk-assistant<br/>Meta-Router"]

    HA --> |"Search queries"| SS["splunk-search"]
    HA --> |"Job management"| SJ["splunk-job"]
    HA --> |"Data export"| SE["splunk-export"]
    HA --> |"Discovery"| SM["splunk-metadata"]
    HA --> |"Lookups"| SL["splunk-lookup"]
    HA --> |"Saved searches"| SSS["splunk-savedsearch"]
    HA --> |"Alerts"| SA["splunk-alert"]
    HA --> |"Security"| SEC["splunk-security"]
    HA --> |"Metrics"| MET["splunk-metrics"]
    HA --> |"Apps"| APP["splunk-app"]
    HA --> |"KV Store"| KV["splunk-kvstore"]
    HA --> |"Tags"| TAG["splunk-tag"]
    HA --> |"REST Admin"| RA["splunk-rest-admin"]

    SS --> SH["Shared Library"]
    SJ --> SH
    SE --> SH
    SM --> SH
    SL --> SH
    SSS --> SH
    SA --> SH
    SEC --> SH
    MET --> SH
    APP --> SH
    KV --> SH
    TAG --> SH
    RA --> SH

    SH --> API["Splunk REST API<br/>Port 8089"]
```

### Technical Highlights

- **Dual Authentication**: JWT Bearer tokens (preferred) and Basic Auth support
- **Environment Config**: Configure via environment variables
- **Search Modes**: Oneshot (ad-hoc), Normal (async), Blocking (sync), Export (streaming)
- **Progressive Disclosure**: 3-level optimization guidance
- **Robust Error Handling**: Custom exception hierarchy with retry logic
- **Type-Safe**: Full type annotations and input validation

---

## Quality & Security

### Test Coverage

| Category | Tests | Description |
|----------|------:|-------------|
| Unit Tests | 180 | Core library and CLI validation |
| Integration Tests | 175 | Live Splunk API verification |
| **Total** | **355** | Comprehensive coverage |

> Tests run against live Splunk instances to ensure real-world reliability.

### Security

- **No credentials in code** — Environment variables or `.local.json` files (gitignored)
- **Token-based auth** — JWT Bearer tokens preferred over Basic Auth
- **Input validation** — All user input sanitized before API calls
- **No destructive defaults** — Explicit confirmation required for dangerous operations

---

## Try It

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/grandcamel/Splunk-Assistant-Skills)

One-click cloud environment with all dependencies pre-installed.

---

## Documentation

| Resource | Description |
|----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Comprehensive project documentation |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| Skill SKILL.md files | Per-skill detailed documentation |
| [splunk-demo](https://github.com/grandcamel/splunk-demo) | Live demo environment with pre-configured Splunk |

### Need Help?

- [GitHub Discussions](https://github.com/grandcamel/Splunk-Assistant-Skills/discussions)
- [Report Issues](https://github.com/grandcamel/Splunk-Assistant-Skills/issues)

---

## E2E Testing

### Run E2E Tests

E2E tests validate the plugin with the Claude Code CLI:

```bash
# Requires ANTHROPIC_API_KEY
./scripts/run-e2e-tests.sh           # Docker
./scripts/run-e2e-tests.sh --local   # Local
```

See [tests/e2e/README.md](tests/e2e/README.md) for details.

---

## Contributing

Contributions are welcome! See our contributing guidelines.

```bash
# Clone the repository
git clone https://github.com/grandcamel/Splunk-Assistant-Skills.git
cd Splunk-Assistant-Skills

# Install dependencies and CLI
pip install -r requirements.txt
pip install -e .

# Run tests (live_integration excluded by default via pytest.ini)
pytest tests/ skills/*/tests/ -v
```

Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## Roadmap

- [ ] **Splunk Cloud** — Native Splunk Cloud API support
- [ ] **Dashboard Skills** — Create and manage dashboards via natural language
- [ ] **Data Model Skills** — Accelerated data model queries
- [ ] **Federated Search** — Cross-instance search capabilities
- [ ] **Workflow Actions** — Trigger external workflows from search results

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Talk to Splunk. Get answers. Ship faster.</strong>
  <br>
  <sub>Built for Claude Code by developers who were tired of memorizing SPL syntax.</sub>
</p>
