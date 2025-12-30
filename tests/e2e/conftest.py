"""Pytest configuration and fixtures for E2E tests."""

import os
import subprocess
import pytest
from pathlib import Path

from .runner import E2ETestRunner, ClaudeCodeRunner


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--e2e-timeout",
        action="store",
        default=os.environ.get("E2E_TEST_TIMEOUT", "120"),
        help="Timeout per test in seconds",
    )
    parser.addoption(
        "--e2e-model",
        action="store",
        default=os.environ.get("E2E_TEST_MODEL", "claude-sonnet-4-20250514"),
        help="Claude model to use",
    )
    parser.addoption(
        "--e2e-verbose",
        action="store_true",
        default=os.environ.get("E2E_VERBOSE", "").lower() == "true",
        help="Enable verbose output",
    )
    parser.addoption(
        "--use-oauth",
        action="store_true",
        default=os.environ.get("E2E_USE_OAUTH", "").lower() == "true",
        help="Use OAuth authentication (ignore ANTHROPIC_API_KEY)",
    )


def _has_oauth_auth() -> bool:
    """Check if OAuth authentication is available."""
    # Check for credentials file
    claude_dir = Path.home() / ".claude"
    if claude_dir.exists() and (claude_dir / "credentials.json").exists():
        return True
    # Check legacy location
    if (Path.home() / ".claude.json").exists():
        return True
    # Check via CLI (with timeout to avoid hanging)
    try:
        result = subprocess.run(
            ["claude", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.fixture(scope="session")
def e2e_enabled():
    """Check if E2E tests should run."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return True
    return _has_oauth_auth()


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def test_cases_path(project_root):
    """Get path to test cases YAML."""
    return project_root / "tests" / "e2e" / "test_cases.yaml"


@pytest.fixture(scope="session")
def e2e_timeout(request):
    """Get E2E test timeout."""
    return int(request.config.getoption("--e2e-timeout"))


@pytest.fixture(scope="session")
def e2e_model(request):
    """Get E2E test model."""
    return request.config.getoption("--e2e-model")


@pytest.fixture(scope="session")
def e2e_verbose(request):
    """Get E2E verbosity setting."""
    return request.config.getoption("--e2e-verbose")


@pytest.fixture(scope="session")
def use_oauth(request):
    """Determine if OAuth should be used (ignoring API key)."""
    # Explicit flag takes precedence
    if request.config.getoption("--use-oauth"):
        return True
    # If no API key set but OAuth is available, use OAuth
    if not os.environ.get("ANTHROPIC_API_KEY") and _has_oauth_auth():
        return True
    return False


@pytest.fixture(scope="session")
def claude_runner(project_root, e2e_timeout, e2e_model, e2e_verbose, e2e_enabled, use_oauth):
    """Create Claude Code runner."""
    if not e2e_enabled:
        pytest.skip("E2E tests disabled (no API key or OAuth credentials)")

    return ClaudeCodeRunner(
        working_dir=project_root,
        timeout=e2e_timeout,
        model=e2e_model,
        verbose=e2e_verbose,
        use_oauth=use_oauth,
    )


@pytest.fixture(scope="session")
def e2e_runner(test_cases_path, project_root, e2e_timeout, e2e_model, e2e_verbose, e2e_enabled, use_oauth):
    """Create E2E test runner."""
    if not e2e_enabled:
        pytest.skip("E2E tests disabled (no API key or OAuth credentials)")

    return E2ETestRunner(
        test_cases_path=test_cases_path,
        working_dir=project_root,
        timeout=e2e_timeout,
        model=e2e_model,
        verbose=e2e_verbose,
        use_oauth=use_oauth,
    )


@pytest.fixture(scope="session")
def installed_plugin(claude_runner, e2e_enabled):
    """Install the plugin once for all tests."""
    if not e2e_enabled:
        pytest.skip("E2E tests disabled")

    result = claude_runner.install_plugin(".")
    if not result["success"] and "already installed" not in result.get("output", "").lower():
        pytest.fail(f"Failed to install plugin: {result.get('error', 'Unknown error')}")

    return result
