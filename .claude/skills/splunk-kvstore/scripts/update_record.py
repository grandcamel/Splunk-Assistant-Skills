#!/usr/bin/env python3
"""Update a record in a KV Store collection."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Update record in KV Store collection")
    parser.add_argument("collection", help="Collection name")
    parser.add_argument("key", help="Record _key value")
    parser.add_argument("data", help="Updated record data as JSON")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    record = json.loads(args.data)
    record["_key"] = args.key  # Ensure key is set

    response = client.post(
        f"/servicesNS/nobody/{args.app}/storage/collections/data/{args.collection}/{args.key}",
        json_body=record,
        operation="update record",
    )

    print_success(f"Record with _key '{args.key}' updated")
    print(format_json(response))


if __name__ == "__main__":
    main()
