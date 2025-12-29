#!/usr/bin/env python3
"""Delete a record from a KV Store collection."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Delete record from KV Store collection"
    )
    parser.add_argument("collection", help="Collection name")
    parser.add_argument("key", help="Record _key value")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    client.delete(
        f"/servicesNS/nobody/{args.app}/storage/collections/data/{args.collection}/{args.key}",
        operation="delete record",
    )

    print_success(f"Record with _key '{args.key}' deleted from '{args.collection}'")


if __name__ == "__main__":
    main()
