#!/usr/bin/env python3
"""
List all tags in Splunk.

Examples:
    python list_tags.py
    python list_tags.py --output json
    python list_tags.py --field host
    python list_tags.py --app search
"""

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
    parser = argparse.ArgumentParser(
        description="List all Splunk tags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python list_tags.py
  python list_tags.py --output json
  python list_tags.py --field host
  python list_tags.py --app search
        """,
    )
    parser.add_argument("--field", "-f", help="Filter by field name")
    parser.add_argument("--app", "-a", help="App context")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    params = {"output_mode": "json", "count": 0}
    if args.app:
        params["namespace"] = args.app

    response = client.get("/saved/fvtags", params=params, operation="list tags")

    tags = []
    for entry in response.get("entry", []):
        name = entry.get("name", "")
        content = entry.get("content", {})
        acl = content.get("eai:acl", {})

        # Parse field::value format
        if "::" in name:
            field, value = name.split("::", 1)
        else:
            field = "unknown"
            value = name

        # Filter by field if specified
        if args.field and field != args.field:
            continue

        tag_list = content.get("tags", [])
        if isinstance(tag_list, str):
            tag_list = [tag_list]

        for tag in tag_list:
            tags.append(
                {
                    "field": field,
                    "value": value,
                    "tag": tag,
                    "app": acl.get("app", "N/A"),
                    "owner": acl.get("owner", "N/A"),
                }
            )

    if args.output == "json":
        print(format_json(tags))
    else:
        if tags:
            print(format_table(tags, columns=["field", "value", "tag", "app", "owner"]))
            print_success(f"Found {len(tags)} tag associations")
        else:
            print_success("No tags found")


if __name__ == "__main__":
    main()
