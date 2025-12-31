#!/usr/bin/env python3
"""
Execute a Splunk search using tag syntax.

Tags allow you to search for events using semantic labels instead of raw field values.

Examples:
    python search_by_tag.py production
    python search_by_tag.py web_traffic --earliest -1h
    python search_by_tag.py production --field host
    python search_by_tag.py internal --field src_ip --output json
"""

import argparse

from splunk_assistant_skills_lib import (
    build_search,
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
        description="Execute a Splunk search using tag syntax",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_by_tag.py production
  python search_by_tag.py web_traffic --earliest -1h
  python search_by_tag.py production --field host
  python search_by_tag.py internal --field src_ip --output json
  python search_by_tag.py database --count 1000 --output csv
        """,
    )
    parser.add_argument("tag", help="Tag to search for")
    parser.add_argument(
        "--field", "-f", help="Specific field to search (e.g., host, sourcetype)"
    )
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time")
    parser.add_argument("--latest", "-l", help="Latest time")
    parser.add_argument("--count", "-c", type=int, help="Maximum results")
    parser.add_argument("--index", "-i", help="Index to search")
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
    max_count = args.count or defaults.get("max_count", 100)

    # Validate inputs
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    # Build SPL query using tag syntax
    if args.field:
        # Field-specific tag search: tag::field=tagname
        tag_search = f"tag::{args.field}={args.tag}"
    else:
        # General tag search: tag=tagname
        tag_search = f"tag={args.tag}"

    # Add index if specified
    if args.index:
        spl = f"index={args.index} {tag_search}"
    else:
        spl = tag_search

    # Build search with time bounds
    search_spl = build_search(spl, earliest_time=earliest, latest_time=latest)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Execute oneshot search
    response = client.post(
        "/search/jobs/oneshot",
        data={
            "search": search_spl,
            "earliest_time": earliest,
            "latest_time": latest,
            "count": max_count,
            "output_mode": "json",
        },
        timeout=api_settings.get("search_timeout", 300),
        operation=f"search by tag {args.tag}",
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
        field_info = f" (field: {args.field})" if args.field else ""
        print_success(f"Found {len(results)} results for tag '{args.tag}'{field_info}")


if __name__ == "__main__":
    main()
