#!/usr/bin/env python3
"""Uninstall a Splunk app."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
    print_warning,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Uninstall Splunk app")
    parser.add_argument("name", help="App name to uninstall")
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    if not args.force:
        print_warning(f"This will permanently remove the app: {args.name}")
        print_warning("All app configurations and data will be deleted.")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            print("Cancelled.")
            return

    client = get_splunk_client(profile=args.profile)

    client.delete(
        f"/services/apps/local/{args.name}",
        operation="uninstall app",
    )

    print_success(f"App '{args.name}' uninstalled successfully")
    print_warning("Splunk may need to be restarted for changes to take full effect")


if __name__ == "__main__":
    main()
