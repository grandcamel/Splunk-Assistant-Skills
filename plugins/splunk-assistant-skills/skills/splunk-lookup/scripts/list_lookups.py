#!/usr/bin/env python3
"""List lookup files in Splunk."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="List Splunk lookup files")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--app", "-a", help="App context")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

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
