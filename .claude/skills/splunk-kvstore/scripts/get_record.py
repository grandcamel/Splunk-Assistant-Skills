#!/usr/bin/env python3
"""Get a record from a KV Store collection by key."""

import sys
import argparse
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Get record from KV Store collection")
    parser.add_argument("collection", help="Collection name")
    parser.add_argument("key", help="Record _key value")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        f"/servicesNS/nobody/{args.app}/storage/collections/data/{args.collection}/{args.key}",
        operation="get record",
    )

    print(format_json(response))
    print_success(f"Retrieved record with _key: {args.key}")


if __name__ == "__main__":
    main()
