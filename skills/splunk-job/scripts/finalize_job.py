#!/usr/bin/env python3
"""Finalize a Splunk search job (stop streaming, return current results)."""

import argparse

from splunk_assistant_skills_lib import (
    finalize_job,
    get_splunk_client,
    handle_errors,
    print_success,
    validate_sid,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Finalize a Splunk search job")
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args(argv)

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)
    finalize_job(client, sid)
    print_success(f"Job finalized: {sid}")


if __name__ == "__main__":
    main()
