#!/usr/bin/env python3
"""List JWT tokens for the authenticated user."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="List JWT tokens for user")
    parser.add_argument("--user", "-u", help="Username (default: current user)")
    parser.add_argument(
        "--count", "-c", type=int, default=100, help="Max results (default: 100)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Build endpoint - tokens can be filtered by user
    endpoint = "/services/authorization/tokens"
    params = {"count": args.count, "output_mode": "json"}

    if args.user:
        # Filter tokens by username
        endpoint = f"/services/authorization/tokens?search=owner={args.user}"

    response = client.get(
        endpoint,
        params=params,
        operation="list tokens",
    )

    entries = response.get("entry", [])

    if args.output == "json":
        print(format_json(entries))
    else:
        display_data = []
        for entry in entries:
            content = entry.get("content", {})
            display_data.append(
                {
                    "ID": content.get("id", "N/A"),
                    "Owner": content.get("owner", "N/A"),
                    "Status": content.get("status", "N/A"),
                    "Audience": content.get("audience", "N/A"),
                    "Created": content.get("claims", {}).get("iat", "N/A"),
                    "Expires": content.get("claims", {}).get("exp", "N/A"),
                }
            )
        if display_data:
            print(format_table(display_data))
        print_success(f"Found {len(entries)} tokens")


if __name__ == "__main__":
    main()
