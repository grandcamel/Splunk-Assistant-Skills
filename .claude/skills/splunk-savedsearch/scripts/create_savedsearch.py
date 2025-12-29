#!/usr/bin/env python3
"""Create a saved search or report."""

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Create saved search")
    parser.add_argument("name", help="Saved search name")
    parser.add_argument("search", help="SPL query")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--description", "-d", help="Description")
    parser.add_argument(
        "--earliest", default="-24h", help="Earliest time (default: -24h)"
    )
    parser.add_argument("--latest", default="now", help="Latest time (default: now)")
    parser.add_argument(
        "--cron", help='Cron schedule (e.g., "0 6 * * *" for 6 AM daily)'
    )
    parser.add_argument("--is-scheduled", action="store_true", help="Enable scheduling")
    parser.add_argument(
        "--alert-type",
        choices=["always", "number of events", "number of hosts", "number of sources"],
        help="Alert trigger condition",
    )
    parser.add_argument("--alert-threshold", help='Alert threshold (e.g., "> 10")')
    parser.add_argument(
        "--actions", help="Comma-separated actions: email,webhook,script"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    data = {
        "name": args.name,
        "search": args.search,
        "dispatch.earliest_time": args.earliest,
        "dispatch.latest_time": args.latest,
    }

    if args.description:
        data["description"] = args.description

    if args.cron:
        data["cron_schedule"] = args.cron
        data["is_scheduled"] = "1"

    if args.is_scheduled:
        data["is_scheduled"] = "1"

    if args.alert_type:
        data["alert_type"] = args.alert_type

    if args.alert_threshold:
        data["alert_threshold"] = args.alert_threshold

    if args.actions:
        data["actions"] = args.actions

    response = client.post(
        f"/servicesNS/nobody/{args.app}/saved/searches",
        data=data,
        operation="create saved search",
    )

    print_success(f"Saved search '{args.name}' created in app '{args.app}'")


if __name__ == "__main__":
    main()
