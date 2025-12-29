#!/usr/bin/env python3
"""Resume a paused Splunk search job."""

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import print_success
from job_poller import unpause_job
from validators import validate_sid


@handle_errors
def main():
    parser = argparse.ArgumentParser(description="Resume a paused Splunk search job")
    parser.add_argument("sid", help="Search job ID")
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    args = parser.parse_args()

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)
    unpause_job(client, sid)
    print_success(f"Job resumed: {sid}")


if __name__ == "__main__":
    main()
