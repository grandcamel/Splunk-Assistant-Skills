#!/usr/bin/env python3
"""
Export raw Splunk events to file.

Streams raw event data efficiently for large exports.
Unlike export_results.py which exports processed results, this exports raw events
with their original _raw field content.

Examples:
    python export_raw.py "index=main" --output raw_events.txt
    python export_raw.py "index=main error" --earliest -1h --output errors.txt
    python export_raw.py "index=main" --earliest -7d --format json --output events.json
"""

import argparse

from splunk_assistant_skills_lib import (
    build_search,
    get_api_settings,
    get_search_defaults,
    get_splunk_client,
    handle_errors,
    print_info,
    print_success,
    validate_spl,
    validate_time_modifier,
    wait_for_job,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Export raw Splunk events to file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("spl", help="SPL query to execute")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument(
        "--format",
        "-f",
        choices=["raw", "json", "xml"],
        default="raw",
        help="Output format (default: raw)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time")
    parser.add_argument("--latest", "-l", help="Latest time")
    parser.add_argument("--progress", action="store_true", help="Show progress")
    args = parser.parse_args(argv)

    # Get defaults
    defaults = get_search_defaults(args.profile)
    api_settings = get_api_settings(args.profile)
    earliest = args.earliest or defaults.get("earliest_time", "-24h")
    latest = args.latest or defaults.get("latest_time", "now")

    # Validate
    spl = validate_spl(args.spl)
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    search_spl = build_search(spl, earliest_time=earliest, latest_time=latest)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Create job
    print_info("Creating search job...")
    response = client.post(
        "/search/v2/jobs",
        data={
            "search": search_spl,
            "exec_mode": "normal",
            "earliest_time": earliest,
            "latest_time": latest,
        },
        operation="create export job",
    )

    sid = response.get("sid")
    if not sid and "entry" in response:
        sid = response["entry"][0].get("name")

    # Wait for completion
    print_info(f"Waiting for job {sid}...")
    progress = wait_for_job(
        client,
        sid,
        timeout=api_settings.get("search_timeout", 300),
        show_progress=args.progress,
    )

    print_info(f"Exporting {progress.event_count:,} raw events...")

    # Build export params
    params = {
        "output_mode": args.format,
        "count": 0,  # All events
    }

    # Stream to file using events endpoint
    bytes_written = 0
    with open(args.output, "wb") as f:
        for chunk in client.stream_results(
            f"/search/v2/jobs/{sid}/events",
            params=params,
            timeout=api_settings.get("search_timeout", 300),
            operation="export raw events",
        ):
            f.write(chunk)
            bytes_written += len(chunk)

    print_success(f"Exported {progress.event_count:,} raw events to {args.output}")
    print_info(f"File size: {bytes_written / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
