#!/usr/bin/env python3
"""List available Splunk indexes."""

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
    parser = argparse.ArgumentParser(description="List Splunk indexes")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    response = client.get("/data/indexes", operation="list indexes")

    indexes = []
    for entry in response.get("entry", []):
        content = entry.get("content", {})
        indexes.append(
            {
                "name": entry.get("name"),
                "totalEventCount": content.get("totalEventCount", 0),
                "currentDBSizeMB": content.get("currentDBSizeMB", 0),
                "maxDataSizeMB": content.get("maxDataSizeMB", 0),
                "disabled": content.get("disabled", False),
            }
        )

    if args.output == "json":
        print(format_json(indexes))
    else:
        display_data = []
        for idx in indexes:
            display_data.append(
                {
                    "Index": idx["name"],
                    "Events": f"{idx['totalEventCount']:,}",
                    "Size (MB)": f"{idx['currentDBSizeMB']:.0f}",
                    "Disabled": "Yes" if idx["disabled"] else "No",
                }
            )
        print(format_table(display_data))
        print_success(f"Found {len(indexes)} indexes")


if __name__ == "__main__":
    main()
