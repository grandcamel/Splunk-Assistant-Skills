#!/usr/bin/env python3
"""Generic GET request to any Splunk REST endpoint."""

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
        description="GET request to Splunk REST endpoint",
        epilog="Example: python rest_get.py /services/server/info",
    )
    parser.add_argument(
        "endpoint", help="REST endpoint path (e.g., /services/server/info)"
    )
    parser.add_argument(
        "--count", "-c", type=int, help="Max results (default: unlimited)"
    )
    parser.add_argument("--search", "-s", help="Search filter (e.g., 'name=admin')")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    # Build query parameters
    params = {"output_mode": "json"}
    if args.count:
        params["count"] = args.count
    if args.search:
        params["search"] = args.search

    # Make the GET request
    endpoint = args.endpoint if args.endpoint.startswith("/") else f"/{args.endpoint}"
    response = client.get(
        endpoint,
        params=params,
        operation=f"GET {endpoint}",
    )

    if args.output == "json":
        print(format_json(response))
    else:
        # Try to format as table if entries exist
        entries = response.get("entry", [])

        if entries:
            display_data = []
            for entry in entries:
                content = entry.get("content", {})
                # Extract key fields
                row = {
                    "Name": entry.get("name", "N/A"),
                    "Title": entry.get("title", "N/A"),
                }

                # Add first few content fields
                for key, value in list(content.items())[:3]:
                    if not key.startswith("eai:"):
                        row[key] = (
                            str(value)[:50]
                            if isinstance(value, (str, int, float))
                            else str(type(value).__name__)
                        )

                display_data.append(row)

            if display_data:
                print(format_table(display_data))
            print_success(f"Retrieved {len(entries)} entries from {endpoint}")
        else:
            # No entries, just print the raw response
            print(format_json(response))
            print_success(f"Retrieved data from {endpoint}")


if __name__ == "__main__":
    main()
