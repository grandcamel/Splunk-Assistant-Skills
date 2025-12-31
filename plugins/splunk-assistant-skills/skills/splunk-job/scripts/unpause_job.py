#!/usr/bin/env python3
"""Resume a paused Splunk search job."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
    unpause_job,
    validate_sid,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Resume a paused Splunk search job")
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args(argv)

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)
    unpause_job(client, sid)
    print_success(f"Job resumed: {sid}")


if __name__ == "__main__":
    main()
