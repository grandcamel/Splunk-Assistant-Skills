#!/usr/bin/env python3
"""Upload a lookup file to Splunk."""

import argparse
from pathlib import Path

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_error,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Upload lookup file")
    parser.add_argument("file", help="Path to CSV file to upload")
    parser.add_argument(
        "--name", "-n", help="Lookup filename in Splunk (defaults to local filename)"
    )
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args(argv)

    file_path = Path(args.file)
    if not file_path.exists():
        print_error(f"File not found: {args.file}")
        return

    lookup_name = args.name or file_path.name

    client = get_splunk_client(profile=args.profile)

    # Read file content
    with open(file_path, "r") as f:
        content = f.read()

    # Upload using multipart form data
    response = client.post(
        f"/servicesNS/nobody/{args.app}/data/lookup-table-files",
        data={
            "name": lookup_name,
            "eai:data": content,
        },
        operation="upload lookup",
    )

    print_success(f"Lookup file '{lookup_name}' uploaded to app '{args.app}'")


if __name__ == "__main__":
    main()
