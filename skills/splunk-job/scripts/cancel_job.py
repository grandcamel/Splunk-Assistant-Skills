#!/usr/bin/env python3
"""
Cancel a running Splunk search job.

Issues the cancel control action to stop a running search.

Examples:
    python cancel_job.py 1703779200.12345
"""

import argparse

from splunk_assistant_skills_lib import (
    cancel_job,
    get_splunk_client,
    handle_errors,
    print_success,
    validate_sid,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Cancel a Splunk search job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args()

    # Validate SID
    sid = validate_sid(args.sid)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Cancel job
    cancel_job(client, sid)
    print_success(f"Job cancelled: {sid}")


if __name__ == "__main__":
    main()
