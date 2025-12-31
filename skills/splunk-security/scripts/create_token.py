#!/usr/bin/env python3
"""Create a new JWT authentication token."""

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
    parser = argparse.ArgumentParser(
        description="Create a new JWT authentication token"
    )
    parser.add_argument("--audience", "-a", help="Token audience (optional)")
    parser.add_argument(
        "--expires-on",
        "-e",
        help="Expiration timestamp (optional, format: YYYY-MM-DD or epoch)",
    )
    parser.add_argument(
        "--not-before",
        "-n",
        help="Not-before timestamp (optional, format: YYYY-MM-DD or epoch)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Build request data
    data = {}
    if args.audience:
        data["audience"] = args.audience
    if args.expires_on:
        data["expires_on"] = args.expires_on
    if args.not_before:
        data["not_before"] = args.not_before

    response = client.post(
        "/services/authorization/tokens",
        data=data,
        operation="create token",
    )

    if args.output == "json":
        print(format_json(response))
    else:
        entry = response.get("entry", [{}])[0]
        content = entry.get("content", {})

        # Display token details
        details = [
            {"Property": "Token ID", "Value": content.get("id", "N/A")},
            {"Property": "Token", "Value": content.get("token", "N/A")},
            {"Property": "Owner", "Value": content.get("owner", "N/A")},
            {"Property": "Status", "Value": content.get("status", "N/A")},
            {"Property": "Audience", "Value": content.get("audience", "N/A")},
            {
                "Property": "Created",
                "Value": content.get("claims", {}).get("iat", "N/A"),
            },
            {
                "Property": "Expires",
                "Value": content.get("claims", {}).get("exp", "N/A"),
            },
        ]
        print(format_table(details))

        # Print the actual token separately for easy copying
        token_value = content.get("token", "")
        if token_value:
            print("\nToken (copy this value):")
            print(token_value)

        print_success("Token created successfully")


if __name__ == "__main__":
    main()
