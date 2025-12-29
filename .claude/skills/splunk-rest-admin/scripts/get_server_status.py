#!/usr/bin/env python3
"""Get Splunk server status and settings."""

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
    parser = argparse.ArgumentParser(description="Get server status")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get("/services/server/status", operation="get server status")

    if args.output == "json":
        print(format_json(response))
    else:
        entry = response.get("entry", [{}])[0]
        content = entry.get("content", {})

        details = [
            {"Property": "Name", "Value": entry.get("name", "N/A")},
        ]

        # Add all content fields dynamically
        for key, value in content.items():
            if not key.startswith("eai:"):
                details.append({"Property": key, "Value": str(value)[:50]})

        print(format_table(details))
        print_success("Retrieved server status")


if __name__ == "__main__":
    main()
