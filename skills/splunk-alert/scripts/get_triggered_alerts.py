#!/usr/bin/env python3
"""List triggered alert instances in Splunk."""

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
    parser = argparse.ArgumentParser(description="List triggered alert instances")
    parser.add_argument(
        "--count", "-c", type=int, default=50, help="Max results (default: 50)"
    )
    parser.add_argument(
        "--severity",
        "-s",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Filter by severity (1=debug, 2=info, 3=warn, 4=error, 5=severe, 6=fatal)",
    )
    parser.add_argument("--savedsearch", help="Filter by saved search name")
    parser.add_argument("--app", "-a", help="Filter by app namespace")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    params = {
        "output_mode": "json",
        "count": args.count,
    }

    response = client.get(
        "/services/alerts/fired_alerts",
        params=params,
        operation="list triggered alerts",
    )

    entries = response.get("entry", [])

    # Filter by severity if specified
    if args.severity:
        entries = [
            e
            for e in entries
            if e.get("content", {}).get("severity", 0) == args.severity
        ]

    # Filter by saved search name if specified
    if args.savedsearch:
        entries = [
            e
            for e in entries
            if args.savedsearch.lower()
            in e.get("content", {}).get("savedsearch_name", "").lower()
        ]

    # Filter by app if specified
    if args.app:
        entries = [e for e in entries if e.get("acl", {}).get("app", "") == args.app]

    if args.output == "json":
        print(format_json(entries))
    else:
        display_data = []
        for entry in entries:
            content = entry.get("content", {})
            acl = entry.get("acl", {})
            display_data.append(
                {
                    "Name": entry.get("name", "N/A"),
                    "Saved Search": content.get("savedsearch_name", "N/A"),
                    "Severity": content.get("severity", "N/A"),
                    "Trigger Time": content.get("trigger_time", "N/A"),
                    "Triggered Count": content.get("triggered_alert_count", 0),
                    "App": acl.get("app", "N/A"),
                }
            )
        if display_data:
            print(format_table(display_data))
        else:
            print("No triggered alerts found.")
        print_success(f"Found {len(entries)} triggered alert instances")


if __name__ == "__main__":
    main()
