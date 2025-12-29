#!/usr/bin/env python3
"""List saved searches in Splunk."""

import sys
import argparse
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_table, format_json, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="List Splunk saved searches")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--app", "-a", help="App context")
    parser.add_argument("--owner", help="Owner filter")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    params = {"count": 0}
    if args.app:
        params["namespace"] = args.app
    if args.owner:
        params["owner"] = args.owner

    response = client.get(
        "/saved/searches", params=params, operation="list saved searches"
    )

    searches = []
    for entry in response.get("entry", []):
        content = entry.get("content", {})
        acl = content.get("eai:acl", {})
        searches.append(
            {
                "name": entry.get("name"),
                "app": acl.get("app", "N/A"),
                "owner": acl.get("owner", "N/A"),
                "scheduled": content.get("is_scheduled", False),
                "disabled": content.get("disabled", False),
            }
        )

    if args.output == "json":
        print(format_json(searches))
    else:
        display_data = []
        for s in searches[:50]:
            display_data.append(
                {
                    "Name": s["name"][:40],
                    "App": s["app"],
                    "Owner": s["owner"],
                    "Scheduled": "Yes" if s["scheduled"] else "No",
                }
            )
        print(format_table(display_data))
        print_success(f"Found {len(searches)} saved searches")


if __name__ == "__main__":
    main()
