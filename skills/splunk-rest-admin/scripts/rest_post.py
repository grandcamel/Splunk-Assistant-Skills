#!/usr/bin/env python3
"""Generic POST request to any Splunk REST endpoint."""

import argparse
import json

from splunk_assistant_skills_lib import (
    format_json,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="POST request to Splunk REST endpoint",
        epilog='Example: python rest_post.py /services/search/jobs --data \'{"search": "index=main | head 10"}\'',
    )
    parser.add_argument(
        "endpoint", help="REST endpoint path (e.g., /services/search/jobs)"
    )
    parser.add_argument(
        "--data",
        "-d",
        help="POST data as JSON string or key=value pairs (e.g., 'search=index=main')",
    )
    parser.add_argument(
        "--file", "-f", help="Read POST data from file (JSON or form-encoded)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Parse POST data
    post_data = {}

    if args.file:
        # Read data from file
        with open(args.file, "r") as f:
            file_content = f.read()
            try:
                post_data = json.loads(file_content)
            except json.JSONDecodeError:
                # Treat as form-encoded key=value pairs
                for line in file_content.strip().split("\n"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        post_data[key.strip()] = value.strip()
    elif args.data:
        # Parse data argument
        try:
            post_data = json.loads(args.data)
        except json.JSONDecodeError:
            # Treat as form-encoded key=value pairs
            for pair in args.data.split("&"):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    post_data[key.strip()] = value.strip()

    # Make the POST request
    endpoint = args.endpoint if args.endpoint.startswith("/") else f"/{args.endpoint}"
    response = client.post(
        endpoint,
        data=post_data,
        operation=f"POST {endpoint}",
    )

    if args.output == "json":
        print(format_json(response))
    else:
        # Try to extract useful information from response
        if isinstance(response, dict):
            # Check for SID (search job creation)
            if "sid" in response:
                print(f"Search Job Created: {response['sid']}")
            elif "entry" in response:
                entries = response.get("entry", [])
                print(f"Entries returned: {len(entries)}")
                if entries and len(entries) == 1:
                    entry = entries[0]
                    print(f"Name: {entry.get('name', 'N/A')}")
                    print(f"Title: {entry.get('title', 'N/A')}")
            else:
                print(format_json(response))
        else:
            print(str(response))

        print_success(f"POST request completed for {endpoint}")


if __name__ == "__main__":
    main()
