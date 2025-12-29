#!/usr/bin/env python3
"""Update an existing saved search."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Update saved search")
    parser.add_argument("name", help="Saved search name")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--search", "-s", help="New SPL query")
    parser.add_argument("--description", "-d", help="New description")
    parser.add_argument("--earliest", help="Earliest time")
    parser.add_argument("--latest", help="Latest time")
    parser.add_argument("--cron", help="New cron schedule")
    parser.add_argument("--enable", action="store_true", help="Enable the saved search")
    parser.add_argument(
        "--disable", action="store_true", help="Disable the saved search"
    )
    parser.add_argument(
        "--enable-schedule", action="store_true", help="Enable scheduling"
    )
    parser.add_argument(
        "--disable-schedule", action="store_true", help="Disable scheduling"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    data = {}

    if args.search:
        data["search"] = args.search

    if args.description:
        data["description"] = args.description

    if args.earliest:
        data["dispatch.earliest_time"] = args.earliest

    if args.latest:
        data["dispatch.latest_time"] = args.latest

    if args.cron:
        data["cron_schedule"] = args.cron

    if args.enable:
        data["disabled"] = "0"
    elif args.disable:
        data["disabled"] = "1"

    if args.enable_schedule:
        data["is_scheduled"] = "1"
    elif args.disable_schedule:
        data["is_scheduled"] = "0"

    if not data:
        print("No updates specified. Use --help for options.")
        return

    response = client.post(
        f"/servicesNS/nobody/{args.app}/saved/searches/{args.name}",
        data=data,
        operation="update saved search",
    )

    print_success(f"Saved search '{args.name}' updated")


if __name__ == "__main__":
    main()
