#!/usr/bin/env python3
"""Get details of a fired alert."""

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, format_table, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Get fired alert details")
    parser.add_argument("name", help="Alert name")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        f"/services/alerts/fired_alerts/{args.name}", operation="get fired alert"
    )

    if args.output == "json":
        print(format_json(response))
    else:
        entry = response.get("entry", [{}])[0]
        content = entry.get("content", {})

        details = [
            {"Property": "Name", "Value": entry.get("name", "N/A")},
            {
                "Property": "Saved Search",
                "Value": content.get("savedsearch_name", "N/A"),
            },
            {"Property": "Severity", "Value": content.get("severity", "N/A")},
            {"Property": "Trigger Time", "Value": content.get("trigger_time", "N/A")},
            {
                "Property": "Triggered Count",
                "Value": content.get("triggered_alert_count", 0),
            },
            {
                "Property": "Expiration Time",
                "Value": content.get("expiration_time", "N/A"),
            },
            {
                "Property": "Digest Mode",
                "Value": "Yes" if content.get("digest_mode") else "No",
            },
        ]
        print(format_table(details))
        print_success(f"Retrieved alert: {args.name}")


if __name__ == "__main__":
    main()
