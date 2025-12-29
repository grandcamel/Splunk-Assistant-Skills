#!/usr/bin/env python3
"""
Execute a Splunk blocking (synchronous) search.

Waits for the search to complete before returning results.
Best for simple queries where you need immediate results.

Examples:
    python search_blocking.py "index=main | head 10"
    python search_blocking.py "index=main | stats count" --timeout 60
"""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_search_results,
    get_api_settings,
    get_search_defaults,
    get_splunk_client,
    handle_errors,
    print_success,
    build_search,
    validate_spl,
    validate_time_modifier,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Execute a Splunk blocking search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("spl", help="SPL query to execute")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time")
    parser.add_argument("--latest", "-l", help="Latest time")
    parser.add_argument(
        "--timeout", "-t", type=int, default=300, help="Timeout in seconds"
    )
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    # Get defaults
    defaults = get_search_defaults(args.profile)
    earliest = args.earliest or defaults.get("earliest_time", "-24h")
    latest = args.latest or defaults.get("latest_time", "now")

    # Validate
    spl = validate_spl(args.spl)
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    search_spl = build_search(spl, earliest_time=earliest, latest_time=latest)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Create blocking job
    response = client.post(
        "/search/v2/jobs",
        data={
            "search": search_spl,
            "exec_mode": "blocking",
            "earliest_time": earliest,
            "latest_time": latest,
        },
        timeout=args.timeout,
        operation="blocking search",
    )

    # Extract SID
    sid = None
    if "entry" in response:
        sid = response["entry"][0].get("name")

    # Get results
    results_response = client.get(
        f"/search/v2/jobs/{sid}/results",
        params={"output_mode": "json", "count": 0},
        operation="get results",
    )

    results = results_response.get("results", [])

    if args.output == "json":
        print(format_json({"sid": sid, "results": results}))
    else:
        print(format_search_results(results))
        print_success(f"Completed: {len(results)} results")


if __name__ == "__main__":
    main()
