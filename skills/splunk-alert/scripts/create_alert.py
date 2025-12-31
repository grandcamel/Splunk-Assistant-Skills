#!/usr/bin/env python3
"""Create an alert from a saved search."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Create alert from saved search")
    parser.add_argument("name", help="Alert/saved search name")
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
    parser.add_argument(
        "--alert-type",
        choices=[
            "always",
            "number of events",
            "number of hosts",
            "number of sources",
            "custom",
        ],
        default="always",
        help="Alert trigger condition (default: always)",
    )
    parser.add_argument(
        "--alert-comparator",
        choices=[
            "greater than",
            "less than",
            "equal to",
            "not equal to",
            "drops by",
            "rises by",
        ],
        help="Alert comparator for threshold",
    )
    parser.add_argument("--alert-threshold", help="Alert threshold value (e.g., 10)")
    parser.add_argument(
        "--severity",
        "-s",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        default=3,
        help="Severity (1=debug, 2=info, 3=warn, 4=error, 5=severe, 6=fatal, default: 3)",
    )
    parser.add_argument(
        "--actions", help="Comma-separated actions: email,webhook,script"
    )
    parser.add_argument("--email-to", help="Email recipient(s) (comma-separated)")
    parser.add_argument("--email-subject", help="Email subject")
    parser.add_argument(
        "--digest-mode",
        action="store_true",
        help="Enable digest mode (combine multiple alerts)",
    )
    parser.add_argument("--throttle", help="Throttle period (e.g., 60s, 5m, 1h)")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    # Build the saved search data with alert configuration
    data = {
        "name": args.name,
        "search": args.search,
        "dispatch.earliest_time": args.earliest,
        "dispatch.latest_time": args.latest,
        "is_scheduled": "1",
        "alert_type": args.alert_type,
        "alert.severity": args.severity,
    }

    if args.description:
        data["description"] = args.description

    if args.cron:
        data["cron_schedule"] = args.cron
    else:
        # Default to run every 5 minutes if no cron specified
        data["cron_schedule"] = "*/5 * * * *"

    # Alert comparator and threshold
    if args.alert_comparator:
        data["alert_comparator"] = args.alert_comparator

    if args.alert_threshold:
        data["alert_threshold"] = args.alert_threshold

    # Alert actions
    if args.actions:
        data["actions"] = args.actions

        # Configure email action if specified
        if "email" in args.actions:
            if args.email_to:
                data["action.email.to"] = args.email_to
            if args.email_subject:
                data["action.email.subject"] = args.email_subject

    # Digest mode
    if args.digest_mode:
        data["alert.digest_mode"] = "1"

    # Throttle
    if args.throttle:
        data["alert.suppress"] = "1"
        data["alert.suppress.period"] = args.throttle

    response = client.post(
        f"/servicesNS/nobody/{args.app}/saved/searches",
        data=data,
        operation="create alert",
    )

    print_success(f"Alert '{args.name}' created in app '{args.app}'")
    if args.cron:
        print_success(f"Schedule: {args.cron}")
    else:
        print_success("Schedule: */5 * * * * (every 5 minutes)")
    print_success(f"Severity: {args.severity}")


if __name__ == "__main__":
    main()
