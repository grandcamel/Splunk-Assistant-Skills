#!/usr/bin/env python3
"""Disable a Splunk app."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
    print_warning,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Disable a Splunk app")
    parser.add_argument("name", help="App name to disable")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Disable the app by setting disabled=1
    data = {"disabled": "1"}

    client.post(
        f"/services/apps/local/{args.name}",
        data=data,
        operation="disable app",
    )

    print_success(f"App '{args.name}' disabled successfully")
    print_warning("Splunk may need to be restarted for changes to take full effect")


if __name__ == "__main__":
    main()
