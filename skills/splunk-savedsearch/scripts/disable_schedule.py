#!/usr/bin/env python3
"""Disable scheduled execution for a saved search."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Disable scheduled execution for a saved search"
    )
    parser.add_argument("name", help="Saved search name")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    data = {"is_scheduled": "0"}

    client.post(
        f"/servicesNS/nobody/{args.app}/saved/searches/{args.name}",
        data=data,
        operation="disable saved search schedule",
    )

    print_success(f"Scheduling disabled for '{args.name}'")


if __name__ == "__main__":
    main()
