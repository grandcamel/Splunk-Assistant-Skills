"""Utility functions for Splunk Assistant Skills CLI."""

import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Optional

# Resolve the skills root directory relative to this file
# This works for both editable installs and regular installs
_THIS_FILE = Path(__file__).resolve()
_SRC_DIR = _THIS_FILE.parent  # src/splunk_assistant_skills/
_PROJECT_ROOT = _SRC_DIR.parent.parent  # Splunk-Assistant-Skills/

SKILLS_ROOT_DIR = _PROJECT_ROOT / "plugins" / "splunk-assistant-skills" / "skills"


def get_script_path(skill_name: str, script_name: str) -> Path:
    """
    Get the full path to a skill script.

    Args:
        skill_name: Name of the skill (e.g., "splunk-search")
        script_name: Name of the script file (e.g., "search_oneshot.py")

    Returns:
        Path to the script file
    """
    return SKILLS_ROOT_DIR / skill_name / "scripts" / script_name


def run_skill_script_subprocess(
    skill_name: str,
    script_name: str,
    args: list[str],
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    """
    Run a skill script via subprocess.

    This is the fallback method when direct import fails.

    Args:
        skill_name: Name of the skill (e.g., "splunk-search")
        script_name: Name of the script file (e.g., "search_oneshot.py")
        args: List of arguments to pass to the script
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess instance with return code and output
    """
    script_path = get_script_path(skill_name, script_name)

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    command = [sys.executable, str(script_path)] + args

    return subprocess.run(
        command,
        capture_output=capture_output,
        text=True,
        check=False,
    )


def try_import_execute_function(
    skill_name: str,
    script_name: str,
) -> Optional[Callable[..., Any]]:
    """
    Try to import the execute function from a skill script.

    Args:
        skill_name: Name of the skill (e.g., "splunk-search")
        script_name: Name of the script file without .py (e.g., "search_oneshot")

    Returns:
        The execute function if found, None otherwise
    """
    # Convert skill name to valid Python module name
    # "splunk-search" -> "splunk_search"
    module_skill_name = skill_name.replace("-", "_")

    # Try to import the module
    try:
        import importlib

        module_path = f"plugins.splunk_assistant_skills.skills.{module_skill_name}.scripts.{script_name}"
        module = importlib.import_module(module_path)

        # Look for execute_* function or main function
        execute_func_name = f"execute_{script_name}"
        if hasattr(module, execute_func_name):
            return getattr(module, execute_func_name)

        # Fallback to main with argv support
        if hasattr(module, "main"):
            return getattr(module, "main")

        return None
    except ImportError:
        return None


def format_output(data: Any, output_format: str = "text") -> str:
    """
    Format output data according to the specified format.

    Args:
        data: Data to format
        output_format: One of "text", "json", "csv"

    Returns:
        Formatted string
    """
    if output_format == "json":
        import json

        return json.dumps(data, indent=2, default=str)
    elif output_format == "csv":
        if isinstance(data, list) and data:
            import csv
            import io

            output = io.StringIO()
            if isinstance(data[0], dict):
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(output)
                writer.writerows(data)
            return output.getvalue()
        return str(data)
    else:
        # text format
        if isinstance(data, (dict, list)):
            import json

            return json.dumps(data, indent=2, default=str)
        return str(data)
