#!/usr/bin/env python3
"""
Query the Splunk metrics catalog.

mcatalog lists available metrics and dimensions in metric indexes.
Useful for discovering what metrics are available in your data.

Examples:
    python mcatalog.py --index metrics
    python mcatalog.py --index metrics --metric cpu.percent
    python mcatalog.py --index metrics --values
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
    validate_time_modifier,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Query the Splunk metrics catalog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcatalog.py --index metrics
  python mcatalog.py --index metrics --metric cpu.percent
  python mcatalog.py --index metrics --values
  python mcatalog.py --index metrics --earliest -7d
        """,
    )
    parser.add_argument("--index", "-i", required=True, help="Metrics index to query")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--metric", "-m", help="Filter by specific metric name")
    parser.add_argument(
        "--values",
        "-v",
        action="store_true",
        help="Show values of metrics (default: count)",
    )
    parser.add_argument("--earliest", "-e", help="Earliest time (default: -24h)")
    parser.add_argument("--latest", "-l", help="Latest time (default: now)")
    parser.add_argument(
        "--count", "-c", type=int, help="Maximum results (default: unlimited)"
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args(argv)

    # Get defaults
    defaults = get_search_defaults(args.profile)
    api_settings = get_api_settings(args.profile)

    earliest = args.earliest or defaults.get("earliest_time", "-24h")
    latest = args.latest or defaults.get("latest_time", "now")

    # Validate time modifiers
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    # Build mcatalog search
    if args.values:
        search_spl = f"| mcatalog values(metric_name) WHERE index={args.index}"
    else:
        search_spl = f"| mcatalog WHERE index={args.index}"

    # Add metric filter if specified
    if args.metric:
        search_spl += f" metric_name={args.metric}"

    # Add count limit if specified
    if args.count:
        search_spl += f" | head {args.count}"

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Execute search
    response = client.post(
        "/search/jobs/oneshot",
        data={
            "search": search_spl,
            "earliest_time": earliest,
            "latest_time": latest,
            "output_mode": "json",
        },
        timeout=api_settings.get("search_timeout", 300),
        operation="mcatalog search",
    )

    # Extract results
    results = response.get("results", [])

    # Output
    if args.output == "json":
        print(format_json(results))
    elif args.output == "csv":
        print(format_search_results(results, output_format="csv"))
    else:
        print(format_search_results(results))
        index_info = f" in index '{args.index}'"
        metric_info = f" for metric '{args.metric}'" if args.metric else ""
        print_success(f"Found {len(results)} results{index_info}{metric_info}")


if __name__ == "__main__":
    main()
