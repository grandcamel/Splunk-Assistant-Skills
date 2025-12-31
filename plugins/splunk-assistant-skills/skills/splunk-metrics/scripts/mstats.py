#!/usr/bin/env python3
"""
Execute a Splunk mstats command for metrics analysis.

mstats is used to query metrics data points with statistical functions.
Best for time series analysis and aggregations on metric data.

Examples:
    python mstats.py "avg(cpu.percent)" --index metrics --by host
    python mstats.py "max(memory.used)" --index metrics --span 1h
    python mstats.py "count()" --index metrics --where "host=server1"
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
        description="Execute a Splunk mstats command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mstats.py "avg(cpu.percent)" --index metrics --by host
  python mstats.py "max(memory.used)" --index metrics --span 1h
  python mstats.py "count()" --index metrics --where "host=server1"
  python mstats.py "avg(cpu.percent)" --index metrics --by host --span 5m --earliest -1h
        """,
    )
    parser.add_argument(
        "metric_function",
        help="Metric function (e.g., avg(cpu.percent), max(memory.used))",
    )
    parser.add_argument("--index", "-i", required=True, help="Metrics index to query")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time (default: -24h)")
    parser.add_argument("--latest", "-l", help="Latest time (default: now)")
    parser.add_argument(
        "--where", "-w", help="WHERE clause filter (e.g., 'host=server1')"
    )
    parser.add_argument(
        "--by", "-b", help="GROUP BY clause (e.g., 'host' or 'host,app')"
    )
    parser.add_argument("--span", "-s", help="Time span for bucketing (e.g., 1h, 5m)")
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

    # Build mstats search
    search_parts = [f"| mstats {args.metric_function}"]

    # Add WHERE clause
    where_conditions = [f"index={args.index}"]
    if args.where:
        where_conditions.append(args.where)
    search_parts.append(f"WHERE {' '.join(where_conditions)}")

    # Add BY clause
    if args.by:
        by_fields = args.by.replace(",", " ")
        search_parts.append(f"BY {by_fields}")

    # Add span
    if args.span:
        search_parts.append(f"span={args.span}")

    search_spl = " ".join(search_parts)

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
        operation="mstats search",
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
        print_success(f"Found {len(results)} results")


if __name__ == "__main__":
    main()
