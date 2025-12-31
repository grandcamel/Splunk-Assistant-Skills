#!/usr/bin/env python3
"""List fired alerts in Splunk."""

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
    parser = argparse.ArgumentParser(description="List fired alerts")
    parser.add_argument(
        "--count", "-c", type=int, default=50, help="Max results (default: 50)"
    )
    parser.add_argument(
        "--severity",
        "-s",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Filter by severity (1=debug to 6=fatal)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    params = {
        "output_mode": "json",
        "count": args.count,
    }

    response = client.get(
        "/services/alerts/fired_alerts", params=params, operation="list fired alerts"
    )

    entries = response.get("entry", [])

    # Filter by severity if specified
    if args.severity:
        entries = [
            e
            for e in entries
            if e.get("content", {}).get("severity", 0) == args.severity
        ]

    if args.output == "json":
        print(format_json(entries))
    else:
        display_data = []
        for entry in entries:
            content = entry.get("content", {})
            display_data.append(
                {
                    "Name": entry.get("name", "N/A"),
                    "Severity": content.get("severity", "N/A"),
                    "Triggered": content.get("triggered_alert_count", 0),
                    "Savedsearch": content.get("savedsearch_name", "N/A"),
                }
            )
        if display_data:
            print(format_table(display_data))
        print_success(f"Found {len(entries)} fired alerts")


if __name__ == "__main__":
    main()
