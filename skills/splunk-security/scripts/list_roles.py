#!/usr/bin/env python3
"""List Splunk roles."""

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
    parser = argparse.ArgumentParser(description="List Splunk roles")
    parser.add_argument(
        "--count", "-c", type=int, default=100, help="Max results (default: 100)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        "/services/authorization/roles",
        params={"count": args.count, "output_mode": "json"},
        operation="list roles",
    )

    entries = response.get("entry", [])

    if args.output == "json":
        print(format_json(entries))
    else:
        display_data = []
        for entry in entries:
            content = entry.get("content", {})
            capabilities = content.get("capabilities", [])
            imported_roles = content.get("imported_roles", [])
            display_data.append(
                {
                    "Role": entry.get("name", "N/A"),
                    "Imported Roles": (
                        ", ".join(imported_roles) if imported_roles else "None"
                    ),
                    "Capabilities": str(len(capabilities)),
                    "Search Filter": (
                        content.get("srchFilter", "None")[:30]
                        if content.get("srchFilter")
                        else "None"
                    ),
                }
            )
        if display_data:
            print(format_table(display_data))
        print_success(f"Found {len(entries)} roles")


if __name__ == "__main__":
    main()
