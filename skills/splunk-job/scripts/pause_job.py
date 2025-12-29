#!/usr/bin/env python3
"""Pause a running Splunk search job."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    pause_job,
    print_success,
    validate_sid,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Pause a Splunk search job")
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args()

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)
    pause_job(client, sid)
    print_success(f"Job paused: {sid}")


if __name__ == "__main__":
    main()
