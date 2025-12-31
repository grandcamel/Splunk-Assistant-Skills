#!/usr/bin/env python3
"""Get details of a saved search."""

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
    parser = argparse.ArgumentParser(description="Get saved search details")
    parser.add_argument("name", help="Saved search name")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        f"/servicesNS/nobody/{args.app}/saved/searches/{args.name}",
        operation="get saved search",
    )

    if args.output == "json":
        print(format_json(response))
    else:
        entry = response.get("entry", [{}])[0]
        content = entry.get("content", {})

        details = [
            {"Property": "Name", "Value": entry.get("name", "N/A")},
            {"Property": "Search", "Value": content.get("search", "N/A")[:100]},
            {
                "Property": "Cron Schedule",
                "Value": content.get("cron_schedule", "Not scheduled"),
            },
            {
                "Property": "Is Scheduled",
                "Value": "Yes" if content.get("is_scheduled") else "No",
            },
            {
                "Property": "Disabled",
                "Value": "Yes" if content.get("disabled") else "No",
            },
            {
                "Property": "Next Run",
                "Value": content.get("next_scheduled_time", "N/A"),
            },
            {"Property": "Actions", "Value": content.get("actions", "None")},
            {"Property": "Alert Type", "Value": content.get("alert_type", "N/A")},
            {
                "Property": "Dispatch Earliest",
                "Value": content.get("dispatch.earliest_time", "N/A"),
            },
            {
                "Property": "Dispatch Latest",
                "Value": content.get("dispatch.latest_time", "N/A"),
            },
        ]
        print(format_table(details))
        print_success(f"Retrieved saved search: {args.name}")


if __name__ == "__main__":
    main()
