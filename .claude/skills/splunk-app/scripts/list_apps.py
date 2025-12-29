#!/usr/bin/env python3
"""List installed Splunk apps."""

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, format_table, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="List Splunk apps")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)
    response = client.get("/apps/local", operation="list apps")

    apps = []
    for entry in response.get("entry", []):
        content = entry.get("content", {})
        apps.append(
            {
                "name": entry.get("name"),
                "label": content.get("label", "N/A"),
                "version": content.get("version", "N/A"),
                "disabled": content.get("disabled", False),
                "visible": content.get("visible", True),
            }
        )

    if args.output == "json":
        print(format_json(apps))
    else:
        display_data = [
            {
                "Name": a["name"],
                "Label": a["label"][:30],
                "Version": a["version"],
                "Enabled": "No" if a["disabled"] else "Yes",
            }
            for a in apps
        ]
        print(format_table(display_data))
        print_success(f"Found {len(apps)} apps")


if __name__ == "__main__":
    main()
