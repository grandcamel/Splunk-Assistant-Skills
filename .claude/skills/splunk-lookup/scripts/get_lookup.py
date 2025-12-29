#!/usr/bin/env python3
"""Get details of a lookup file."""

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
    parser = argparse.ArgumentParser(description="Get lookup file details")
    parser.add_argument("name", help="Lookup filename in Splunk")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        f"/servicesNS/nobody/{args.app}/data/lookup-table-files/{args.name}",
        operation="get lookup",
    )

    if args.output == "json":
        print(format_json(response))
    else:
        entry = response.get("entry", [{}])[0]
        content = entry.get("content", {})

        details = [
            {"Property": "Name", "Value": entry.get("name", "N/A")},
            {"Property": "App", "Value": content.get("eai:appName", args.app)},
            {"Property": "Path", "Value": content.get("eai:data", "N/A")},
            {"Property": "Owner", "Value": entry.get("author", "N/A")},
        ]
        print(format_table(details))
        print_success(f"Retrieved lookup: {args.name}")


if __name__ == "__main__":
    main()
