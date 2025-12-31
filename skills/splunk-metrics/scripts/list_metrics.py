#!/usr/bin/env python3
"""List available metric names in a Splunk metrics index."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_api_settings,
    get_search_defaults,
    get_splunk_client,
    handle_errors,
    print_success,
    validate_time_modifier,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="List metric names in a metrics index",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python list_metrics.py --index metrics
  python list_metrics.py --index metrics --count 50
  python list_metrics.py --index metrics --earliest -7d
        """,
    )
    parser.add_argument("--index", "-i", required=True, help="Metrics index to query")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time (default: -24h)")
    parser.add_argument("--latest", "-l", help="Latest time (default: now)")
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=100,
        help="Maximum results (default: 100)",
    )
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    # Get defaults
    defaults = get_search_defaults(args.profile)
    api_settings = get_api_settings(args.profile)

    earliest = args.earliest or defaults.get("earliest_time", "-24h")
    latest = args.latest or defaults.get("latest_time", "now")

    # Validate time modifiers
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    # Build search to list metric names
    # Using mcatalog to get unique metric names
    search_spl = f"| mcatalog values(metric_name) WHERE index={args.index} | mvexpand metric_name | dedup metric_name | sort metric_name | head {args.count}"

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
        operation="list metrics",
    )

    # Extract results
    results = response.get("results", [])

    if args.output == "json":
        print(format_json(results))
    else:
        # Format as simple table
        display_data = [{"Metric Name": r.get("metric_name", "N/A")} for r in results]
        print(format_table(display_data))
        print_success(f"Found {len(results)} metrics in index '{args.index}'")


if __name__ == "__main__":
    main()
