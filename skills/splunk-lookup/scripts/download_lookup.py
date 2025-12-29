#!/usr/bin/env python3
"""Download a lookup file from Splunk."""

import argparse

from splunk_assistant_skills_lib import get_splunk_client, handle_errors, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Download lookup file")
    parser.add_argument("name", help="Lookup filename in Splunk")
    parser.add_argument(
        "--output", "-o", help="Output file path (defaults to lookup name)"
    )
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Get lookup content - need to use raw response
    response = client.session.get(
        f"{client.base_url}/servicesNS/nobody/{args.app}/data/lookup-table-files/{args.name}",
        params={"output_mode": "csv"},
        verify=client.verify_ssl,
    )
    response.raise_for_status()

    output_path = args.output or args.name
    with open(output_path, "w") as f:
        f.write(response.text)

    print_success(f"Lookup file '{args.name}' downloaded to '{output_path}'")


if __name__ == "__main__":
    main()
