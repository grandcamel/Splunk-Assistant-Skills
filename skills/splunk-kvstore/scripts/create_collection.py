#!/usr/bin/env python3
"""Create a KV Store collection."""

import argparse
import json

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Create KV Store collection")
    parser.add_argument("name", help="Collection name")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument(
        "--fields",
        "-f",
        help='Field definitions as JSON: {"field1": "string", "field2": "number"}',
    )
    parser.add_argument(
        "--accelerated-fields",
        help='Accelerated fields as JSON: {"index_name": {"field1": 1}}',
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    data = {"name": args.name}

    # Add field definitions if provided
    if args.fields:
        fields = json.loads(args.fields)
        for field_name, field_type in fields.items():
            data[f"field.{field_name}"] = field_type

    # Add accelerated fields if provided
    if args.accelerated_fields:
        accel = json.loads(args.accelerated_fields)
        for index_name, index_def in accel.items():
            data[f"accelerated_fields.{index_name}"] = json.dumps(index_def)

    response = client.post(
        f"/servicesNS/nobody/{args.app}/storage/collections/config",
        data=data,
        operation="create collection",
    )

    print_success(f"Collection '{args.name}' created in app '{args.app}'")


if __name__ == "__main__":
    main()
