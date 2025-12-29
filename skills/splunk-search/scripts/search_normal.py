#!/usr/bin/env python3
"""
Execute a Splunk normal (async) search.

Creates a search job that runs asynchronously. Returns the SID for polling.
Use --wait to block until completion and show results.

Examples:
    python search_normal.py "index=main | stats count by sourcetype"
    python search_normal.py "index=main" --wait --timeout 300
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
    wait_for_job,
    build_search,
    validate_spl,
    validate_time_modifier,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Execute a Splunk normal (async) search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("spl", help="SPL query to execute")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time")
    parser.add_argument("--latest", "-l", help="Latest time")
    parser.add_argument("--wait", "-w", action="store_true", help="Wait for completion")
    parser.add_argument(
        "--timeout", "-t", type=int, default=300, help="Wait timeout (seconds)"
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

    # Get client and create job
    client = get_splunk_client(profile=args.profile)

    response = client.post(
        "/search/v2/jobs",
        data={
            "search": search_spl,
            "exec_mode": "normal",
            "earliest_time": earliest,
            "latest_time": latest,
        },
        operation="create search job",
    )

    sid = response.get("sid")
    if not sid and "entry" in response:
        sid = response["entry"][0].get("name")

    if args.wait:
        # Wait for completion
        progress = wait_for_job(client, sid, timeout=args.timeout, show_progress=True)

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
    else:
        if args.output == "json":
            print(format_json({"sid": sid, "status": "created"}))
        else:
            print_success(f"Job created: {sid}")
            print(f"Use: python poll_job.py {sid}")


if __name__ == "__main__":
    main()
