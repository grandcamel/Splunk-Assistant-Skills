#!/usr/bin/env python3
"""Enable scheduled execution for a saved search."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Enable scheduled execution for a saved search"
    )
    parser.add_argument("name", help="Saved search name")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--cron", help="Cron schedule (optional, e.g., '0 * * * *')")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    data = {"is_scheduled": "1"}

    if args.cron:
        data["cron_schedule"] = args.cron

    client.post(
        f"/servicesNS/nobody/{args.app}/saved/searches/{args.name}",
        data=data,
        operation="enable saved search schedule",
    )

    if args.cron:
        print_success(
            f"Scheduling enabled for '{args.name}' with cron schedule: {args.cron}"
        )
    else:
        print_success(f"Scheduling enabled for '{args.name}'")


if __name__ == "__main__":
    main()
