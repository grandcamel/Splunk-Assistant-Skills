#!/usr/bin/env python3
"""List KV Store collections."""

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
    parser = argparse.ArgumentParser(description="List KV Store collections")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)
    response = client.get(
        f"/servicesNS/nobody/{args.app}/storage/collections/config",
        operation="list collections",
    )

    collections = []
    for entry in response.get("entry", []):
        content = entry.get("content", {})
        collections.append(
            {
                "name": entry.get("name"),
                "app": content.get("eai:appName", args.app),
                "field_count": len(
                    [k for k in content.keys() if k.startswith("field.")]
                ),
                "accelerated": content.get("accelerated_fields", {}) != {},
            }
        )

    if args.output == "json":
        print(format_json(collections))
    else:
        display_data = [
            {
                "Collection": c["name"],
                "App": c["app"],
                "Fields": c["field_count"],
                "Accelerated": "Yes" if c["accelerated"] else "No",
            }
            for c in collections
        ]
        print(format_table(display_data))
        print_success(f"Found {len(collections)} collections in app '{args.app}'")


if __name__ == "__main__":
    main()
