#!/usr/bin/env python3
"""Install a Splunk app from file or Splunkbase."""

import sys
import argparse
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import print_success, print_warning


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Install Splunk app")
    parser.add_argument(
        "source", help="App package path (.tar.gz/.tgz/.spl) or Splunkbase app ID"
    )
    parser.add_argument(
        "--name", "-n", help="App name (auto-detected from package if not specified)"
    )
    parser.add_argument(
        "--update", "-u", action="store_true", help="Update if app already exists"
    )
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    source_path = Path(args.source)
    is_file = source_path.exists() and source_path.is_file()

    if not is_file and not args.source.isdigit():
        print_warning(
            f"Source '{args.source}' is not a valid file path or Splunkbase app ID"
        )
        return

    if not args.force:
        if is_file:
            print_warning(f"This will install app from file: {args.source}")
        else:
            print_warning(f"This will install app from Splunkbase ID: {args.source}")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            print("Cancelled.")
            return

    client = get_splunk_client(profile=args.profile)

    if is_file:
        # Install from local file
        with open(source_path, "rb") as f:
            file_content = f.read()

        data = {
            "name": args.name
            or source_path.stem.replace(".tar", "").replace(".spl", ""),
            "update": "1" if args.update else "0",
        }

        # Use multipart form upload
        response = client.post(
            "/services/apps/local",
            data=data,
            files={"appfile": (source_path.name, file_content)},
            operation="install app from file",
        )
    else:
        # Install from Splunkbase
        data = {
            "name": args.source,  # Splunkbase app ID
            "update": "1" if args.update else "0",
        }

        response = client.post(
            "/services/apps/local", data=data, operation="install app from Splunkbase"
        )

    print_success(f"App installed successfully from: {args.source}")


if __name__ == "__main__":
    main()
