#!/usr/bin/env python3
"""
List Splunk search jobs.

Lists all search jobs for the current user with status and details.

Examples:
    python list_jobs.py
    python list_jobs.py --count 20
    python list_jobs.py --output json
"""

import argparse
import sys
from pathlib import Path

# Add shared lib to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, format_table
from job_poller import list_jobs


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="List Splunk search jobs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=50,
        help="Maximum number of jobs to list (default: 50)",
    )
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    # Get client
    client = get_splunk_client(profile=args.profile)

    # List jobs
    jobs = list_jobs(client, count=args.count)

    if args.output == "json":
        print(format_json(jobs))
    else:
        if not jobs:
            print("No active jobs found.")
            return

        # Format for display
        display_data = []
        for job in jobs:
            display_data.append(
                {
                    "SID": job.get("sid", "")[:30],
                    "State": job.get("dispatchState", "Unknown"),
                    "Progress": f"{float(job.get('doneProgress', 0)) * 100:.0f}%",
                    "Results": job.get("resultCount", 0),
                    "Duration": f"{float(job.get('runDuration', 0)):.1f}s",
                }
            )

        print(
            format_table(
                display_data,
                columns=["SID", "State", "Progress", "Results", "Duration"],
            )
        )
        print(f"\nTotal: {len(jobs)} jobs")


if __name__ == "__main__":
    main()
