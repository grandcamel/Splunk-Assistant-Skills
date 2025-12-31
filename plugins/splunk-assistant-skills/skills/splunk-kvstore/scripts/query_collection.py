#!/usr/bin/env python3
"""Query records from a KV Store collection."""

import argparse
import json

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Query KV Store collection")
    parser.add_argument("collection", help="Collection name")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument(
        "--filter", "-f", help='Query filter as JSON: {"field": "value"}'
    )
    parser.add_argument("--fields", help="Comma-separated list of fields to return")
    parser.add_argument(
        "--sort", "-s", help="Sort field (prefix with - for descending)"
    )
    parser.add_argument(
        "--limit", "-l", type=int, default=100, help="Max records (default: 100)"
    )
    parser.add_argument("--skip", type=int, default=0, help="Records to skip (offset)")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    params = {
        "output_mode": "json",
        "limit": args.limit,
        "skip": args.skip,
    }

    if args.filter:
        params["query"] = args.filter

    if args.fields:
        params["fields"] = args.fields

    if args.sort:
        params["sort"] = args.sort

    response = client.get(
        f"/servicesNS/nobody/{args.app}/storage/collections/data/{args.collection}",
        params=params,
        operation="query collection",
    )

    # Response is a list of records
    records = response if isinstance(response, list) else []

    if args.output == "json":
        print(format_json(records))
    else:
        if records:
            # Get all keys from first record for display
            display_data = []
            for r in records:
                row = {"_key": r.get("_key", "N/A")}
                for k, v in r.items():
                    if k not in ("_key", "_user"):
                        row[k] = str(v)[:50] if isinstance(v, str) else v
                display_data.append(row)
            print(format_table(display_data))
        print_success(f"Found {len(records)} records in '{args.collection}'")


if __name__ == "__main__":
    main()
