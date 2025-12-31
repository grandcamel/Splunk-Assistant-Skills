#!/usr/bin/env python3
"""Acknowledge/delete a fired alert instance."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
    print_warning,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Acknowledge/delete a fired alert")
    parser.add_argument("name", help="Alert name")
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args(argv)

    if not args.force:
        print_warning(f"This will acknowledge/delete fired alert '{args.name}'")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            print("Cancelled.")
            return

    client = get_splunk_client(profile=args.profile)

    client.delete(
        f"/services/alerts/fired_alerts/{args.name}", operation="acknowledge alert"
    )

    print_success(f"Alert '{args.name}' acknowledged/deleted")


if __name__ == "__main__":
    main()
