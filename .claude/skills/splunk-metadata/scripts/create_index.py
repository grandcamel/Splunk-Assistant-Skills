#!/usr/bin/env python3
"""Create a new Splunk index."""

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Create Splunk index")
    parser.add_argument("name", help="Index name")
    parser.add_argument(
        "--datatype",
        "-d",
        choices=["event", "metric"],
        default="event",
        help="Index datatype (default: event)",
    )
    parser.add_argument("--max-size-mb", type=int, help="Maximum total size in MB")
    parser.add_argument("--frozen-time", type=int, help="Frozen time period in seconds")
    parser.add_argument("--home-path", help="Home path for hot/warm buckets")
    parser.add_argument("--cold-path", help="Cold path for cold buckets")
    parser.add_argument("--profile", "-p", help="Splunk profile")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    data = {
        "name": args.name,
        "datatype": args.datatype,
    }

    if args.max_size_mb:
        data["maxTotalDataSizeMB"] = args.max_size_mb

    if args.frozen_time:
        data["frozenTimePeriodInSecs"] = args.frozen_time

    if args.home_path:
        data["homePath"] = args.home_path

    if args.cold_path:
        data["coldPath"] = args.cold_path

    response = client.post("/data/indexes", data=data, operation="create index")

    print_success(f"Index '{args.name}' created (datatype: {args.datatype})")


if __name__ == "__main__":
    main()
