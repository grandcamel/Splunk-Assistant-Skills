#!/usr/bin/env python3
"""
Poll a Splunk search job until completion.

Waits for a job to reach terminal state (DONE or FAILED) with progress updates.

Examples:
    python poll_job.py 1703779200.12345
    python poll_job.py 1703779200.12345 --timeout 300
    python poll_job.py 1703779200.12345 --quiet
"""

import sys
import argparse
from pathlib import Path

# Add shared lib to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from validators import validate_sid
from formatters import print_success, format_json
from job_poller import wait_for_job


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Poll Splunk search job until completion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python poll_job.py 1703779200.12345
  python poll_job.py 1703779200.12345 --timeout 300
  python poll_job.py 1703779200.12345 --quiet
        """,
    )
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress updates"
    )
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    # Validate SID
    sid = validate_sid(args.sid)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Wait for job completion
    progress = wait_for_job(
        client,
        sid,
        timeout=args.timeout,
        show_progress=not args.quiet,
    )

    if args.output == "json":
        print(
            format_json(
                {
                    "sid": progress.sid,
                    "state": progress.state.value,
                    "result_count": progress.result_count,
                    "event_count": progress.event_count,
                    "run_duration": progress.run_duration,
                }
            )
        )
    else:
        print_success(f"Job completed: {progress.state.value}")
        print(f"Results: {progress.result_count:,}")
        print(f"Events: {progress.event_count:,}")
        print(f"Duration: {progress.run_duration:.2f}s")


if __name__ == "__main__":
    main()
