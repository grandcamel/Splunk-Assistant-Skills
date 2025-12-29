#!/usr/bin/env python3
"""
Create a new Splunk search job.

Creates a search job and returns the SID for subsequent operations.
The job runs asynchronously - use poll_job.py to wait for completion.

Examples:
    python create_job.py "index=main | stats count by sourcetype"
    python create_job.py "index=main | head 100" --earliest -1h --latest now
    python create_job.py "index=main" --blocking
"""

import argparse
import sys
from pathlib import Path

# Add shared lib to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_search_defaults, get_splunk_client
from error_handler import handle_errors
from formatters import format_json, print_success
from spl_helper import build_search
from validators import validate_spl, validate_time_modifier


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Create a Splunk search job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_job.py "index=main | stats count"
  python create_job.py "index=main | head 100" --earliest -1h
  python create_job.py "index=main" --exec-mode blocking
        """,
    )
    parser.add_argument("spl", help="SPL query to execute")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time (default: from config)")
    parser.add_argument("--latest", "-l", help="Latest time (default: from config)")
    parser.add_argument(
        "--exec-mode",
        choices=["normal", "blocking"],
        default="normal",
        help="Execution mode (default: normal)",
    )
    parser.add_argument("--app", help="App context for search")
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    # Get defaults
    defaults = get_search_defaults(args.profile)
    earliest = args.earliest or defaults.get("earliest_time", "-24h")
    latest = args.latest or defaults.get("latest_time", "now")

    # Validate inputs
    spl = validate_spl(args.spl)
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    # Build search with time bounds
    search_spl = build_search(spl, earliest_time=earliest, latest_time=latest)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Build request data
    data = {
        "search": search_spl,
        "exec_mode": args.exec_mode,
        "earliest_time": earliest,
        "latest_time": latest,
    }

    if args.app:
        data["namespace"] = args.app

    # Create job
    response = client.post(
        "/search/v2/jobs",
        data=data,
        timeout=(
            client.DEFAULT_SEARCH_TIMEOUT
            if args.exec_mode == "blocking"
            else client.timeout
        ),
        operation="create search job",
    )

    # Extract SID
    sid = response.get("sid")
    if not sid and "entry" in response:
        sid = response["entry"][0].get(
            "name", response["entry"][0].get("content", {}).get("sid")
        )

    if args.output == "json":
        print(
            format_json(
                {
                    "sid": sid,
                    "exec_mode": args.exec_mode,
                    "search": search_spl,
                    "earliest_time": earliest,
                    "latest_time": latest,
                }
            )
        )
    else:
        print_success(f"Job created: {sid}")
        print(f"Search: {search_spl[:80]}{'...' if len(search_spl) > 80 else ''}")
        print(f"Mode: {args.exec_mode}")
        print(f"Time range: {earliest} to {latest}")


if __name__ == "__main__":
    main()
