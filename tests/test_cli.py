"""Tests for the Splunk Assistant Skills CLI."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from splunk_assistant_skills.cli.main import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestCLIRoot:
    """Tests for the root CLI command."""

    def test_version(self, runner):
        """Test --version flag."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_help(self, runner):
        """Test --help flag."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Splunk Assistant Skills CLI" in result.output
        assert "search" in result.output
        assert "job" in result.output
        assert "export" in result.output

    def test_no_command_shows_help(self, runner):
        """Test that no command shows help."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Usage:" in result.output


class TestSearchCommands:
    """Tests for search command group."""

    def test_search_help(self, runner):
        """Test search --help."""
        result = runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0
        assert "oneshot" in result.output
        assert "normal" in result.output
        assert "blocking" in result.output

    @patch("splunk_assistant_skills.cli.commands.search_cmds.run_skill_script_subprocess")
    def test_search_oneshot(self, mock_run, runner):
        """Test search oneshot command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, ["search", "oneshot", "index=main | head 10"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0]
        assert args[0] == "splunk-search"
        assert args[1] == "search_oneshot.py"
        assert "index=main | head 10" in args[2]

    @patch("splunk_assistant_skills.cli.commands.search_cmds.run_skill_script_subprocess")
    def test_search_oneshot_with_options(self, mock_run, runner):
        """Test search oneshot with options."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, [
            "search", "oneshot", "index=main",
            "--earliest", "-1h",
            "--latest", "now",
            "--output", "json"
        ])

        assert result.exit_code == 0
        args = mock_run.call_args[0][2]
        assert "--earliest" in args
        assert "-1h" in args
        assert "--output" in args
        assert "json" in args

    @patch("splunk_assistant_skills.cli.commands.search_cmds.run_skill_script_subprocess")
    def test_search_validate(self, mock_run, runner):
        """Test search validate command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, ["search", "validate", "index=main | stats count"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0]
        assert args[1] == "validate_spl.py"


class TestJobCommands:
    """Tests for job command group."""

    def test_job_help(self, runner):
        """Test job --help."""
        result = runner.invoke(cli, ["job", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output
        assert "status" in result.output
        assert "cancel" in result.output

    @patch("splunk_assistant_skills.cli.commands.job_cmds.run_skill_script_subprocess")
    def test_job_status(self, mock_run, runner):
        """Test job status command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, ["job", "status", "1703779200.12345"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0]
        assert args[1] == "get_job_status.py"
        assert "1703779200.12345" in args[2]

    @patch("splunk_assistant_skills.cli.commands.job_cmds.run_skill_script_subprocess")
    def test_job_cancel(self, mock_run, runner):
        """Test job cancel command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, ["job", "cancel", "1703779200.12345"])

        assert result.exit_code == 0
        args = mock_run.call_args[0]
        assert args[1] == "cancel_job.py"


class TestMetadataCommands:
    """Tests for metadata command group."""

    def test_metadata_help(self, runner):
        """Test metadata --help."""
        result = runner.invoke(cli, ["metadata", "--help"])
        assert result.exit_code == 0
        assert "indexes" in result.output
        assert "sourcetypes" in result.output

    @patch("splunk_assistant_skills.cli.commands.metadata_cmds.run_skill_script_subprocess")
    def test_metadata_indexes(self, mock_run, runner):
        """Test metadata indexes command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, ["metadata", "indexes"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0]
        assert args[1] == "list_indexes.py"


class TestExportCommands:
    """Tests for export command group."""

    def test_export_help(self, runner):
        """Test export --help."""
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0
        assert "results" in result.output
        assert "raw" in result.output

    @patch("splunk_assistant_skills.cli.commands.export_cmds.run_skill_script_subprocess")
    def test_export_results(self, mock_run, runner):
        """Test export results command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, [
            "export", "results", "1703779200.12345",
            "--output-file", "results.csv"
        ])

        assert result.exit_code == 0
        args = mock_run.call_args[0]
        assert args[1] == "export_results.py"
        assert "--output-file" in args[2]


class TestAdminCommands:
    """Tests for admin command group."""

    def test_admin_help(self, runner):
        """Test admin --help."""
        result = runner.invoke(cli, ["admin", "--help"])
        assert result.exit_code == 0
        assert "info" in result.output
        assert "status" in result.output
        assert "health" in result.output

    @patch("splunk_assistant_skills.cli.commands.admin_cmds.run_skill_script_subprocess")
    def test_admin_info(self, mock_run, runner):
        """Test admin info command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, ["admin", "info"])

        assert result.exit_code == 0
        args = mock_run.call_args[0]
        assert args[1] == "get_server_info.py"


class TestSecurityCommands:
    """Tests for security command group."""

    def test_security_help(self, runner):
        """Test security --help."""
        result = runner.invoke(cli, ["security", "--help"])
        assert result.exit_code == 0
        assert "whoami" in result.output
        assert "list-tokens" in result.output

    @patch("splunk_assistant_skills.cli.commands.security_cmds.run_skill_script_subprocess")
    def test_security_whoami(self, mock_run, runner):
        """Test security whoami command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = runner.invoke(cli, ["security", "whoami"])

        assert result.exit_code == 0
        args = mock_run.call_args[0]
        assert args[1] == "get_current_user.py"


class TestErrorHandling:
    """Tests for CLI error handling."""

    @patch("splunk_assistant_skills.cli.commands.search_cmds.run_skill_script_subprocess")
    def test_script_failure_propagates_exit_code(self, mock_run, runner):
        """Test that script failure exit code is propagated."""
        mock_run.return_value = MagicMock(returncode=1)

        result = runner.invoke(cli, ["search", "oneshot", "index=main"])

        assert result.exit_code == 1

    def test_invalid_command(self, runner):
        """Test invalid command shows error."""
        result = runner.invoke(cli, ["invalid_command"])
        assert result.exit_code != 0
        assert "No such command" in result.output or "Error" in result.output
