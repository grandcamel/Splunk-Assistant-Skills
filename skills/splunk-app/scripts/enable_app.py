#!/usr/bin/env python3
"""Enable a disabled Splunk app."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
    print_warning,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Enable a disabled Splunk app")
    parser.add_argument("name", help="App name to enable")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Enable the app by setting disabled=0
    data = {"disabled": "0"}

    client.post(
        f"/services/apps/local/{args.name}",
        data=data,
        operation="enable app",
    )

    print_success(f"App '{args.name}' enabled successfully")
    print_warning("Splunk may need to be restarted for changes to take full effect")


if __name__ == "__main__":
    main()
