#!/usr/bin/env python3
"""Get details of a Splunk app."""

import sys
import argparse
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, format_table, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Get app details")
    parser.add_argument("name", help="App name")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(f"/services/apps/local/{args.name}", operation="get app")

    if args.output == "json":
        print(format_json(response))
    else:
        entry = response.get("entry", [{}])[0]
        content = entry.get("content", {})

        details = [
            {"Property": "Name", "Value": entry.get("name", "N/A")},
            {"Property": "Label", "Value": content.get("label", "N/A")},
            {"Property": "Version", "Value": content.get("version", "N/A")},
            {"Property": "Author", "Value": content.get("author", "N/A")},
            {
                "Property": "Description",
                "Value": (content.get("description", "N/A") or "N/A")[:60],
            },
            {"Property": "Visible", "Value": "Yes" if content.get("visible") else "No"},
            {
                "Property": "Disabled",
                "Value": "Yes" if content.get("disabled") else "No",
            },
            {
                "Property": "Configured",
                "Value": "Yes" if content.get("configured") else "No",
            },
            {
                "Property": "Check for Updates",
                "Value": "Yes" if content.get("check_for_updates") else "No",
            },
        ]
        print(format_table(details))
        print_success(f"Retrieved app: {args.name}")


if __name__ == "__main__":
    main()
