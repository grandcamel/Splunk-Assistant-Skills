#!/usr/bin/env python3
"""
Migration script to update imports from vendored library to PyPI package.
"""

import os
import re
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPING = {
    "config_manager": "splunk_as",
    "error_handler": "splunk_as",
    "formatters": "splunk_as",
    "validators": "splunk_as",
    "spl_helper": "splunk_as",
    "job_poller": "splunk_as",
    "time_utils": "splunk_as",
    "splunk_client": "splunk_as",
}

# Pattern to match sys.path.insert for shared lib
SYS_PATH_PATTERNS = [
    r"^import sys\n",
    r"^from pathlib import Path\n",
    r"^# Add shared lib to path\n",
    r'^sys\.path\.insert\(\s*\n?\s*0,\s*str\(Path\(__file__\)\.parent\.parent\.parent / "shared" / "scripts" / "lib"\)\s*\)\n?',
    r'^sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent / "scripts" / "lib"\)\)\n?',
    r'^sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\.parent / "shared" / "scripts" / "lib"\)\)\n?',
]


def process_file(filepath: Path) -> bool:
    """Process a single file and update imports."""
    try:
        content = filepath.read_text()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    original_content = content

    # Remove sys.path.insert patterns (multi-line)
    # Pattern for scripts in skills/*/scripts/
    content = re.sub(
        r'import sys\nfrom pathlib import Path\n\n# Add shared lib to path\nsys\.path\.insert\(\n\s*0, str\(Path\(__file__\)\.parent\.parent\.parent / "shared" / "scripts" / "lib"\)\n\)\n\n',
        "",
        content,
    )

    # Pattern for scripts (single line variant)
    content = re.sub(
        r'import sys\nfrom pathlib import Path\n\nsys\.path\.insert\(\n\s*0, str\(Path\(__file__\)\.parent\.parent\.parent / "shared" / "scripts" / "lib"\)\n\)\n\n',
        "",
        content,
    )

    # Pattern for tests
    content = re.sub(
        r'import sys\nfrom pathlib import Path\n\nimport pytest\n\nsys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent / "scripts" / "lib"\)\)\n\n',
        "import pytest\n\n",
        content,
    )

    # Pattern for tests (conftest.py style)
    content = re.sub(
        r'import sys\nfrom pathlib import Path\n(.*?)\n\n# Add shared lib to path\nsys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\.parent / "shared" / "scripts" / "lib"\)\)\n',
        r"\1\n",
        content,
        flags=re.DOTALL,
    )

    # More general patterns
    content = re.sub(
        r"^import sys\n^from pathlib import Path\n\n^sys\.path\.insert.*\n\n",
        "",
        content,
        flags=re.MULTILINE,
    )

    # Update import statements
    # from config_manager import X -> from splunk_as import X
    for old_module in IMPORT_MAPPING:
        content = re.sub(
            rf"^from {old_module} import (.+)$",
            r"from splunk_as import \1",
            content,
            flags=re.MULTILINE,
        )

    # Handle validators.ValidationError specifically (there's a class in both)
    # The error_handler.ValidationError takes precedence
    content = re.sub(
        r"from splunk_as import \(([^)]*?)ValidationError,([^)]*?)\)",
        r"from splunk_as import (\1ValidationError as ValidatorValidationError,\2)",
        content,
        flags=re.DOTALL,
    )

    if content != original_content:
        try:
            filepath.write_text(content)
            print(f"Updated: {filepath}")
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    return False


def main():
    """Main function."""
    skills_dir = Path(__file__).parent.parent / "skills"

    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}")
        return

    updated = 0
    for py_file in skills_dir.rglob("*.py"):
        # Skip __pycache__
        if "__pycache__" in str(py_file):
            continue
        # Skip the library files themselves
        if "shared/scripts/lib" in str(py_file):
            continue

        if process_file(py_file):
            updated += 1

    print(f"\nUpdated {updated} files")


if __name__ == "__main__":
    main()
