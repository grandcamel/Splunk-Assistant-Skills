#!/usr/bin/env python3
"""Get Splunk server information."""

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Get Splunk server info")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)
    info = client.get_server_info()

    if args.output == "json":
        print(format_json(info))
    else:
        print(f"Server:     {info.get('serverName', 'Unknown')}")
        print(f"Version:    {info.get('version', 'Unknown')}")
        print(f"Build:      {info.get('build', 'Unknown')}")
        print(
            f"OS:         {info.get('os_name', 'Unknown')} {info.get('os_version', '')}"
        )
        print(f"License:    {info.get('licenseState', 'Unknown')}")
        print(f"Mode:       {info.get('serverRoles', ['Unknown'])}")
        print_success("Server info retrieved")


if __name__ == "__main__":
    main()
