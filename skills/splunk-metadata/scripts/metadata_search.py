#!/usr/bin/env python3
"""Execute Splunk metadata search."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Execute metadata search")
    parser.add_argument(
        "type",
        choices=["sources", "sourcetypes", "hosts"],
        help="Metadata type to search",
    )
    parser.add_argument("--index", "-i", help="Filter by index")
    parser.add_argument(
        "--count", "-c", type=int, default=100, help="Max results (default: 100)"
    )
    parser.add_argument(
        "--earliest",
        "-e",
        default="-24h",
        help="Earliest time (default: -24h)",
    )
    parser.add_argument(
        "--latest",
        "-l",
        default="now",
        help="Latest time (default: now)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Build metadata search
    search = f"| metadata type={args.type}"
    if args.index:
        search += f" index={args.index}"
    search += f" | sort -totalCount | head {args.count}"

    response = client.post(
        "/search/jobs/oneshot",
        data={
            "search": search,
            "output_mode": "json",
            "earliest_time": args.earliest,
            "latest_time": args.latest,
        },
        operation="metadata search",
    )

    results = response.get("results", [])

    if args.output == "json":
        print(format_json(results))
    else:
        # Determine the key field based on type
        key_field = args.type.rstrip("s")  # sources -> source, hosts -> host, etc.

        display_data = []
        for r in results:
            display_data.append(
                {
                    "Item": r.get(key_field, "N/A"),
                    "Total Count": r.get("totalCount", 0),
                    "Recent Total Count": r.get("recentTotalCount", 0),
                    "First Time": (
                        r.get("firstTime", "N/A")[:19] if r.get("firstTime") else "N/A"
                    ),
                    "Last Time": (
                        r.get("lastTime", "N/A")[:19] if r.get("lastTime") else "N/A"
                    ),
                }
            )
        print(format_table(display_data))
        index_info = f" in index '{args.index}'" if args.index else ""
        print_success(f"Found {len(results)} {args.type}{index_info}")


if __name__ == "__main__":
    main()
