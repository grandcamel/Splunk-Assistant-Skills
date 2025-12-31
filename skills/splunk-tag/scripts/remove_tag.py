#!/usr/bin/env python3
"""
Remove a tag from a field value in Splunk.

Examples:
    python remove_tag.py --field host --value webserver01 --tag production
    python remove_tag.py --field sourcetype --value access_combined --tag web_traffic
"""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_error,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Remove a tag from a field value",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python remove_tag.py --field host --value webserver01 --tag production
  python remove_tag.py --field sourcetype --value access_combined --tag web_traffic
  python remove_tag.py --field host --value dbserver01 --tag production --app search
        """,
    )
    parser.add_argument("--field", "-f", required=True, help="Field name")
    parser.add_argument("--value", "-v", required=True, help="Field value")
    parser.add_argument(
        "--tag",
        "-t",
        action="append",
        required=True,
        help="Tag(s) to remove (can specify multiple times)",
    )
    parser.add_argument(
        "--app", "-a", default="search", help="App context (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args()

    if not args.field or not args.value:
        print_error("Field and value are required")
        return

    if not args.tag:
        print_error("At least one tag is required")
        return

    client = get_splunk_client(profile=args.profile)

    # Tag endpoint format: /services/saved/fvtags/{field}::{value}
    tag_name = f"{args.field}::{args.value}"

    # Get existing tags
    try:
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
        print_error(f"No tags found for {args.field}={args.value}")
        return

    # Remove specified tags
    remaining_tags = [tag for tag in existing_tags if tag not in args.tag]

    if len(remaining_tags) == len(existing_tags):
        print_error(
            f"Tag(s) {', '.join(args.tag)} not found on {args.field}={args.value}"
        )
        return

    # Update or delete the tag entry
    if remaining_tags:
        # Update with remaining tags
        client.post(
            f"/saved/fvtags/{tag_name}",
            data={
                "value": ",".join(remaining_tags),
                "output_mode": "json",
            },
            params={"namespace": args.app},
            operation=f"update tags for {tag_name}",
        )
        print_success(
            f"Removed tag(s) {', '.join(args.tag)} from {args.field}={args.value} (remaining: {', '.join(remaining_tags)})"
        )
    else:
        # No tags left, delete the entry
        client.delete(
            f"/saved/fvtags/{tag_name}",
            params={"namespace": args.app},
            operation=f"delete tag entry {tag_name}",
        )
        print_success(f"Removed all tags from {args.field}={args.value}")


if __name__ == "__main__":
    main()
