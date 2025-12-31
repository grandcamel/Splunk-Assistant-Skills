#!/usr/bin/env python3
"""List metric-type Splunk indexes."""

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
    parser = argparse.ArgumentParser(description="List metric indexes")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    # Get all indexes
    response = client.get("/data/indexes", operation="list indexes")

    # Filter for metric indexes (datatype=metric)
    metric_indexes = []
    for entry in response.get("entry", []):
        content = entry.get("content", {})
        # Metric indexes have datatype="metric"
        if content.get("datatype") == "metric":
            metric_indexes.append(
                {
                    "name": entry.get("name"),
                    "totalEventCount": content.get("totalEventCount", 0),
                    "currentDBSizeMB": content.get("currentDBSizeMB", 0),
                    "maxDataSizeMB": content.get("maxDataSizeMB", 0),
                    "disabled": content.get("disabled", False),
                    "datatype": content.get("datatype", ""),
                }
            )

    if args.output == "json":
        print(format_json(metric_indexes))
    else:
        display_data = []
        for idx in metric_indexes:
            display_data.append(
                {
                    "Index": idx["name"],
                    "Events": f"{idx['totalEventCount']:,}",
                    "Size (MB)": f"{idx['currentDBSizeMB']:.0f}",
                    "Disabled": "Yes" if idx["disabled"] else "No",
                }
            )
        print(format_table(display_data))
        print_success(f"Found {len(metric_indexes)} metric indexes")


if __name__ == "__main__":
    main()
