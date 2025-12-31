#!/usr/bin/env python3
"""Get preview results from a running Splunk search job."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_search_results,
    get_splunk_client,
    handle_errors,
    validate_sid,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Get preview results from a running job"
    )
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument(
        "--count", "-c", type=int, default=100, help="Max preview results"
    )
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)

    response = client.get(
        f"/search/v2/jobs/{sid}/results_preview",
        params={"output_mode": "json", "count": args.count},
        operation="get preview",
    )

    results = response.get("results", [])

    if args.output == "json":
        print(format_json(results))
    else:
        print(format_search_results(results))
        print(f"Preview: {len(results)} results (job may still be running)")


if __name__ == "__main__":
    main()
