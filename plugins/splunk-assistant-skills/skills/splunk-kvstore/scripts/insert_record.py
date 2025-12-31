#!/usr/bin/env python3
"""Insert a record into a KV Store collection."""

import argparse
import json

from splunk_assistant_skills_lib import (
    format_json,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Insert record into KV Store collection"
    )
    parser.add_argument("collection", help="Collection name")
    parser.add_argument(
        "data", help='Record data as JSON: {"field1": "value1", "field2": 123}'
    )
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument(
        "--key", "-k", help="Specify _key value (auto-generated if not provided)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    record = json.loads(args.data)
    if args.key:
        record["_key"] = args.key

    response = client.post(
        f"/servicesNS/nobody/{args.app}/storage/collections/data/{args.collection}",
        json_body=record,
        operation="insert record",
    )

    # Response contains the _key of the inserted record
    key = response.get("_key", "unknown")
    print_success(f"Record inserted with _key: {key}")
    print(format_json(response))


if __name__ == "__main__":
    main()
