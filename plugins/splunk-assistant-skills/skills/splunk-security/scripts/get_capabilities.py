#!/usr/bin/env python3
"""Get capabilities for a specific user or current user."""

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
    parser = argparse.ArgumentParser(description="Get user capabilities")
    parser.add_argument("--user", "-u", help="Username (default: current user)")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    if args.user:
        # Get specific user information
        response = client.get(
            f"/services/authentication/users/{args.user}",
            params={"output_mode": "json"},
            operation=f"get user {args.user}",
        )
    else:
        # Get current user context
        response = client.get(
            "/services/authentication/current-context",
            params={"output_mode": "json"},
            operation="get current user",
        )

    entry = response.get("entry", [{}])[0]
    content = entry.get("content", {})

    username = content.get("username", "N/A")
    capabilities = content.get("capabilities", [])
    roles = content.get("roles", [])

    if args.output == "json":
        result = {
            "username": username,
            "roles": roles,
            "capabilities": capabilities,
        }
        print(format_json(result))
    else:
        # Display user info
        user_info = [
            {"Property": "Username", "Value": username},
            {"Property": "Roles", "Value": ", ".join(roles)},
            {"Property": "Total Capabilities", "Value": str(len(capabilities))},
        ]
        print(format_table(user_info))

        # Display capabilities in a table format
        if capabilities:
            print("\nCapabilities:")
            cap_data = [{"Capability": cap} for cap in sorted(capabilities)]
            print(format_table(cap_data))

        print_success(f"Found {len(capabilities)} capabilities for user '{username}'")


if __name__ == "__main__":
    main()
