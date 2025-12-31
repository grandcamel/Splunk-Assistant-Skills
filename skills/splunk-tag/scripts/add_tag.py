#!/usr/bin/env python3
"""
Add a tag to a field value in Splunk.

Tags allow you to assign semantic meaning to field values, making them easier to search.

Examples:
    python add_tag.py --field host --value webserver01 --tag production
    python add_tag.py --field sourcetype --value access_combined --tag web_traffic
    python add_tag.py --field host --value dbserver01 --tag production --tag database
"""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_error,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Add a tag to a field value",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_tag.py --field host --value webserver01 --tag production
  python add_tag.py --field sourcetype --value access_combined --tag web_traffic
  python add_tag.py --field host --value dbserver01 --tag production --tag database --app search
        """,
    )
    parser.add_argument("--field", "-f", required=True, help="Field name")
    parser.add_argument("--value", "-v", required=True, help="Field value to tag")
    parser.add_argument(
        "--tag",
        "-t",
        action="append",
        required=True,
        help="Tag(s) to add (can specify multiple times)",
    )
    parser.add_argument(
        "--app", "-a", default="search", help="App context (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args(argv)

    if not args.field or not args.value:
        print_error("Field and value are required")
        return

    if not args.tag:
        print_error("At least one tag is required")
        return

    client = get_splunk_client(profile=args.profile)

    # Tag endpoint format: /services/saved/fvtags/{field}::{value}
    tag_name = f"{args.field}::{args.value}"

    # Check if tag already exists, if not create it
    try:
        # Try to get existing tags
        response = client.get(
            f"/saved/fvtags/{tag_name}",
            params={"output_mode": "json"},
            operation=f"get tags for {tag_name}",
        )
        existing_tags = []
        for entry in response.get("entry", []):
            content = entry.get("content", {})
            existing_tags.extend(content.get("tags", []))
    except Exception:
        # Tag doesn't exist yet, will be created
        existing_tags = []

    # Combine with new tags
    all_tags = list(set(existing_tags + args.tag))

    # Create or update the tag
    try:
        client.post(
            f"/saved/fvtags/{tag_name}",
            data={
                "value": ",".join(all_tags),
                "output_mode": "json",
            },
            params={"namespace": args.app},
            operation=f"add tags to {tag_name}",
        )
        print_success(
            f"Added tag(s) {', '.join(args.tag)} to {args.field}={args.value} (total tags: {', '.join(all_tags)})"
        )
    except Exception as e:
        print_error(f"Failed to add tags: {e}")


if __name__ == "__main__":
    main()
