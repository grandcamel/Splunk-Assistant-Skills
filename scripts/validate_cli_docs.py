#!/usr/bin/env python3
"""Validate that CLI examples in SKILL.md files match actual splunk-as commands.

This script:
1. Parses all skills/*/SKILL.md files
2. Extracts CLI command examples (lines starting with 'splunk-as')
3. Runs 'splunk-as <command> --help' to verify the command exists
4. Reports any documented commands that don't exist in the CLI
5. Exits with non-zero status if validation fails

Usage:
    python scripts/validate_cli_docs.py
    python scripts/validate_cli_docs.py --verbose
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Known top-level command groups from splunk-as --help
KNOWN_GROUPS = {
    'admin', 'alert', 'app', 'export', 'job', 'kvstore',
    'lookup', 'metadata', 'metrics', 'savedsearch', 'search',
    'security', 'tag'
}


def extract_cli_commands(skill_md_path: Path) -> list[tuple[str, int]]:
    """Extract splunk-as commands from a SKILL.md file.

    Returns list of (command, line_number) tuples.
    Only extracts commands that match known command groups.
    """
    commands = []
    content = skill_md_path.read_text()

    for line_num, line in enumerate(content.splitlines(), start=1):
        # Match lines that contain splunk-as commands
        # Look for 'splunk-as' followed by command words
        match = re.search(r'splunk-as\s+(\S+)(?:\s+(\S+))?', line)
        if match:
            group = match.group(1).strip('`')
            subcommand = match.group(2).strip('`') if match.group(2) else None

            # Only process known command groups
            if group not in KNOWN_GROUPS:
                continue

            # If there's a subcommand that looks like a valid subcommand name
            if subcommand and not (
                subcommand.startswith('-') or
                subcommand.startswith('"') or
                subcommand.startswith("'") or
                subcommand.startswith('<') or
                re.match(r'^\d+\.', subcommand) or  # SID pattern
                re.match(r'^[A-Z]', subcommand)  # Uppercase (likely placeholder)
            ):
                command = f"{group} {subcommand}"
            else:
                command = group

            commands.append((command, line_num))

    return commands


def validate_command(command: str) -> bool:
    """Check if a splunk-as command exists by running --help.

    Returns True if command exists, False otherwise.
    """
    try:
        # Split command into parts for subprocess
        cmd_parts = ["splunk-as"] + command.split() + ["--help"]
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=10
        )
        # Check for explicit "No such command" error message
        if "No such command" in result.stderr or "No such command" in result.stdout:
            return False
        # Command exists if it returns 0 and shows help
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  Warning: Timeout checking '{command}'")
        return False
    except Exception as e:
        print(f"  Warning: Error checking '{command}': {e}")
        return False


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate CLI examples in SKILL.md files"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show all commands being validated'
    )
    args = parser.parse_args()

    # Find all SKILL.md files
    base_path = Path(__file__).parent.parent
    skill_files = list(base_path.glob("skills/*/SKILL.md"))

    if not skill_files:
        print("No SKILL.md files found in skills/*/")
        sys.exit(1)

    print(f"Found {len(skill_files)} SKILL.md files to validate")
    print()

    # Track all commands and validation results
    all_errors = []
    validated_commands = set()  # Cache to avoid re-validating same commands
    command_results = {}  # Cache validation results

    for skill_file in sorted(skill_files):
        skill_name = skill_file.parent.name
        commands = extract_cli_commands(skill_file)

        if not commands:
            continue

        print(f"Checking {skill_name}...")

        for command, line_num in commands:
            # Skip if already validated
            if command in validated_commands:
                if not command_results[command]:
                    all_errors.append((skill_file, command, line_num))
                elif args.verbose:
                    print(f"  OK (cached): splunk-as {command}")
                continue

            validated_commands.add(command)
            is_valid = validate_command(command)
            command_results[command] = is_valid

            if not is_valid:
                all_errors.append((skill_file, command, line_num))
                print(f"  ERROR: '{command}' not found (line {line_num})")
            elif args.verbose:
                print(f"  OK: splunk-as {command}")

    print()

    # Summary
    total_commands = len(validated_commands)
    failed_commands = len([c for c, v in command_results.items() if not v])

    print(f"Validated {total_commands} unique commands")

    if all_errors:
        print()
        print("=" * 60)
        print("VALIDATION FAILED")
        print("=" * 60)
        print()
        print("The following documented commands do not exist:")
        print()

        # Group errors by file
        errors_by_file = {}
        for skill_file, command, line_num in all_errors:
            if skill_file not in errors_by_file:
                errors_by_file[skill_file] = []
            errors_by_file[skill_file].append((command, line_num))

        for skill_file, errors in sorted(errors_by_file.items()):
            print(f"{skill_file.relative_to(base_path)}:")
            for command, line_num in errors:
                print(f"  Line {line_num}: splunk-as {command}")
            print()

        print(f"Total: {failed_commands} invalid command(s)")
        sys.exit(1)
    else:
        print("All documented commands are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
