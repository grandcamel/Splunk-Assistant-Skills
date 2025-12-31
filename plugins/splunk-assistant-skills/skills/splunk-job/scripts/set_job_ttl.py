#!/usr/bin/env python3
"""Set the time-to-live (TTL) for a Splunk search job."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
    set_job_ttl,
    validate_sid,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Set TTL for a Splunk search job")
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument(
        "--ttl",
        "-t",
        type=int,
        default=3600,
        help="Time-to-live in seconds (default: 3600)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args(argv)

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)
    set_job_ttl(client, sid, args.ttl)
    print_success(f"TTL set to {args.ttl}s for job: {sid}")


if __name__ == "__main__":
    main()
