#!/usr/bin/env python3
"""Get field summary for a Splunk index or sourcetype."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Get field summary")
    parser.add_argument("--index", "-i", help="Filter by index")
    parser.add_argument("--sourcetype", "-s", help="Filter by sourcetype")
    parser.add_argument(
        "--maxvals",
        "-m",
        type=int,
        default=10,
        help="Max distinct values per field (default: 10)",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1000,
        help="Sample size for analysis (default: 1000)",
    )
    parser.add_argument(
        "--earliest",
        "-e",
        default="-1h",
        help="Earliest time (default: -1h)",
    )
    parser.add_argument(
        "--latest",
        "-l",
        default="now",
        help="Latest time (default: now)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    # Build search query
    search_parts = []
    if args.index:
        search_parts.append(f"index={args.index}")
    if args.sourcetype:
        search_parts.append(f"sourcetype={args.sourcetype}")

    if not search_parts:
        search_parts.append("index=*")

    search = "search " + " ".join(search_parts)
    search += f" | head {args.count} | fieldsummary maxvals={args.maxvals}"

    response = client.post(
        "/search/jobs/oneshot",
        data={
            "search": search,
            "output_mode": "json",
            "earliest_time": args.earliest,
            "latest_time": args.latest,
        },
        operation="field summary",
    )

    results = response.get("results", [])

    if args.output == "json":
        print(format_json(results))
    else:
        display_data = []
        for r in results:
            # Parse values if present
            values = r.get("values", [])
            if isinstance(values, list) and len(values) > 0:
                value_str = ", ".join([str(v) for v in values[:3]])
                if len(values) > 3:
                    value_str += f" ... (+{len(values) - 3} more)"
            else:
                value_str = "N/A"

            display_data.append(
                {
                    "Field": r.get("field", "N/A"),
                    "Count": r.get("count", 0),
                    "Distinct": r.get("distinct_count", 0),
                    "% Present": (
                        f"{float(r.get('count', 0)) / args.count * 100:.1f}%"
                        if r.get("count")
                        else "0.0%"
                    ),
                    "Sample Values": value_str,
                }
            )

        # Sort by count descending
        display_data.sort(key=lambda x: int(x["Count"]), reverse=True)

        print(format_table(display_data))

        filter_info = []
        if args.index:
            filter_info.append(f"index={args.index}")
        if args.sourcetype:
            filter_info.append(f"sourcetype={args.sourcetype}")
        filter_str = " ".join(filter_info) if filter_info else "all data"

        print_success(f"Found {len(results)} fields for {filter_str}")


if __name__ == "__main__":
    main()
