#!/usr/bin/env python3
"""Estimate result count before export."""

import sys
import argparse
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client, get_search_defaults
from error_handler import handle_errors
from validators import validate_spl, validate_time_modifier
from formatters import print_success, format_json
from spl_helper import build_search
from job_poller import wait_for_job


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Estimate export size")
    parser.add_argument("spl", help="SPL query")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--earliest", "-e", help="Earliest time")
    parser.add_argument("--latest", "-l", help="Latest time")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    defaults = get_search_defaults(args.profile)
    earliest = args.earliest or defaults.get("earliest_time", "-24h")
    latest = args.latest or defaults.get("latest_time", "now")

    spl = validate_spl(args.spl)
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    # Add stats count to estimate
    count_spl = f"{spl} | stats count"
    search_spl = build_search(count_spl, earliest_time=earliest, latest_time=latest)

    client = get_splunk_client(profile=args.profile)

    response = client.post(
        "/search/jobs/oneshot",
        data={
            "search": search_spl,
            "earliest_time": earliest,
            "latest_time": latest,
            "output_mode": "json",
        },
        operation="estimate size",
    )

    results = response.get("results", [])
    count = int(results[0].get("count", 0)) if results else 0

    if args.output == "json":
        print(format_json({"estimated_count": count}))
    else:
        print_success(f"Estimated results: {count:,}")


if __name__ == "__main__":
    main()
