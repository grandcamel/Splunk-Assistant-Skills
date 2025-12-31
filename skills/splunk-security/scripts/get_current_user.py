#!/usr/bin/env python3
"""Get current authenticated user context."""

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
    parser = argparse.ArgumentParser(description="Get current user context")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        "/services/authentication/current-context", operation="get current user"
    )

    if args.output == "json":
        print(format_json(response))
    else:
        entry = response.get("entry", [{}])[0]
        content = entry.get("content", {})

        details = [
            {"Property": "Username", "Value": content.get("username", "N/A")},
            {"Property": "Real Name", "Value": content.get("realname", "N/A")},
            {"Property": "Email", "Value": content.get("email", "N/A")},
            {"Property": "Roles", "Value": ", ".join(content.get("roles", []))},
            {
                "Property": "Capabilities",
                "Value": str(len(content.get("capabilities", []))) + " capabilities",
            },
            {"Property": "Default App", "Value": content.get("defaultApp", "N/A")},
        ]
        print(format_table(details))
        print_success(f"Current user: {content.get('username', 'N/A')}")


if __name__ == "__main__":
    main()
