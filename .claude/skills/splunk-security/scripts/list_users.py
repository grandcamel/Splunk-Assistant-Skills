#!/usr/bin/env python3
"""List Splunk users."""

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
    parser = argparse.ArgumentParser(description="List Splunk users")
    parser.add_argument(
        "--count", "-c", type=int, default=100, help="Max results (default: 100)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        "/services/authentication/users",
        params={"count": args.count, "output_mode": "json"},
        operation="list users",
    )

    entries = response.get("entry", [])

    if args.output == "json":
        print(format_json(entries))
    else:
        display_data = []
        for entry in entries:
            content = entry.get("content", {})
            display_data.append(
                {
                    "Username": entry.get("name", "N/A"),
                    "Real Name": content.get("realname", "N/A"),
                    "Email": content.get("email", "N/A"),
                    "Roles": ", ".join(content.get("roles", [])),
                    "Default App": content.get("defaultApp", "N/A"),
                }
            )
        if display_data:
            print(format_table(display_data))
        print_success(f"Found {len(entries)} users")


if __name__ == "__main__":
    main()
