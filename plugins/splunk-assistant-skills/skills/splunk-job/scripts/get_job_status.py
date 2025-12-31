#!/usr/bin/env python3
"""
Get the status of a Splunk search job.

Retrieves current state, progress, and statistics for a search job.

Examples:
    python get_job_status.py 1703779200.12345
    python get_job_status.py 1703779200.12345 --output json
"""

import argparse

from splunk_assistant_skills_lib import (
    format_job_status,
    format_json,
    get_dispatch_state,
    get_splunk_client,
    handle_errors,
    validate_sid,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Get Splunk search job status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_job_status.py 1703779200.12345
  python get_job_status.py 1703779200.12345 --output json
        """,
    )
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args(argv)

    # Validate SID
    sid = validate_sid(args.sid)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Get job status
    progress = get_dispatch_state(client, sid)

    if args.output == "json":
        print(
            format_json(
                {
                    "sid": progress.sid,
                    "state": progress.state.value,
                    "progress": progress.progress_percent,
                    "event_count": progress.event_count,
                    "result_count": progress.result_count,
                    "scan_count": progress.scan_count,
                    "run_duration": progress.run_duration,
                    "is_done": progress.is_done,
                    "is_failed": progress.is_failed,
                    "is_paused": progress.is_paused,
                }
            )
        )
    else:
        print(format_job_status({"content": progress.data}))


if __name__ == "__main__":
    main()
