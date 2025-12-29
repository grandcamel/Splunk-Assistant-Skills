#!/usr/bin/env python3
"""
Get results from a completed Splunk search job.

Retrieves results from a job that has reached DONE state.

Examples:
    python get_results.py 1703779200.12345
    python get_results.py 1703779200.12345 --count 100 --offset 0
    python get_results.py 1703779200.12345 --fields host,status
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from validators import validate_sid
from formatters import format_search_results, format_json, export_csv, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Get results from a Splunk search job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument(
        "--count", "-c", type=int, default=0, help="Max results (0=all)"
    )
    parser.add_argument("--offset", type=int, default=0, help="Result offset")
    parser.add_argument("--fields", "-f", help="Comma-separated fields")
    parser.add_argument(
        "--output", "-o", choices=["text", "json", "csv"], default="text"
    )
    parser.add_argument("--output-file", help="Write to file")
    args = parser.parse_args()

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)

    # Build params
    params = {
        "output_mode": "json",
        "count": args.count,
        "offset": args.offset,
    }

    if args.fields:
        params["field_list"] = args.fields

    # Get results
    response = client.get(
        f"/search/v2/jobs/{sid}/results",
        params=params,
        operation="get results",
    )

    results = response.get("results", [])
    fields = args.fields.split(",") if args.fields else None

    if args.output == "json":
        print(format_json(results))
    elif args.output == "csv":
        if args.output_file:
            export_csv(results, args.output_file, columns=fields)
            print_success(f"Written to {args.output_file}")
        else:
            print(format_search_results(results, fields=fields, output_format="csv"))
    else:
        print(format_search_results(results, fields=fields))
        print_success(f"Retrieved {len(results)} results")


if __name__ == "__main__":
    main()
