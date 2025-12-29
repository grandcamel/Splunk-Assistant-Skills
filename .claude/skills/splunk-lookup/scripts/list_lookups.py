#!/usr/bin/env python3
"""List lookup files in Splunk."""

import sys
import argparse
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_table, format_json, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="List Splunk lookup files")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--app", "-a", help="App context")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    params = {}
    if args.app:
        params["namespace"] = args.app

    response = client.get(
        "/data/lookup-table-files", params=params, operation="list lookups"
    )

    lookups = []
    for entry in response.get("entry", []):
        content = entry.get("content", {})
        acl = content.get("eai:acl", {})
        lookups.append(
            {
                "name": entry.get("name"),
                "app": acl.get("app", "N/A"),
                "owner": acl.get("owner", "N/A"),
            }
        )

    if args.output == "json":
        print(format_json(lookups))
    else:
        print(format_table(lookups, columns=["name", "app", "owner"]))
        print_success(f"Found {len(lookups)} lookup files")


if __name__ == "__main__":
    main()
