#!/usr/bin/env python3
"""Run a saved search on-demand (dispatch)."""

import sys
import argparse
import time
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import print_success, print_info, format_json


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Run saved search on-demand")
    parser.add_argument("name", help="Saved search name")
    parser.add_argument(
        "--app", "-a", default="search", help="App namespace (default: search)"
    )
    parser.add_argument("--wait", "-w", action="store_true", help="Wait for completion")
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=300,
        help="Wait timeout in seconds (default: 300)",
    )
    parser.add_argument("--earliest", help="Override earliest time")
    parser.add_argument("--latest", help="Override latest time")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    data = {}
    if args.earliest:
        data["dispatch.earliest_time"] = args.earliest
    if args.latest:
        data["dispatch.latest_time"] = args.latest

    response = client.post(
        f"/servicesNS/nobody/{args.app}/saved/searches/{args.name}/dispatch",
        data=data if data else None,
        operation="dispatch saved search",
    )

    sid = response.get("sid")
    print_success(f"Saved search '{args.name}' dispatched with SID: {sid}")

    if args.wait and sid:
        print_info("Waiting for completion...")
        start = time.time()
        while time.time() - start < args.timeout:
            status = client.get(f"/search/v2/jobs/{sid}", operation="check status")
            content = status.get("entry", [{}])[0].get("content", {})
            if content.get("isDone"):
                print_success(
                    f"Search completed. Results: {content.get('resultCount', 0)}"
                )

                if args.output == "json":
                    results = client.get(
                        f"/search/v2/jobs/{sid}/results",
                        params={"output_mode": "json"},
                        operation="get results",
                    )
                    print(format_json(results.get("results", [])))
                break
            time.sleep(2)
        else:
            print_info(
                f"Timeout after {args.timeout}s. Job still running with SID: {sid}"
            )


if __name__ == "__main__":
    main()
