#!/usr/bin/env python3
"""Set the time-to-live (TTL) for a Splunk search job."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from validators import validate_sid
from formatters import print_success
from job_poller import set_job_ttl


@handle_errors
def main():
    parser = argparse.ArgumentParser(description='Set TTL for a Splunk search job')
    parser.add_argument('sid', help='Search job ID')
    parser.add_argument('--ttl', '-t', type=int, default=3600,
                       help='Time-to-live in seconds (default: 3600)')
    parser.add_argument('--profile', '-p', help='Splunk profile to use')
    args = parser.parse_args()

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)
    set_job_ttl(client, sid, args.ttl)
    print_success(f"TTL set to {args.ttl}s for job: {sid}")


if __name__ == '__main__':
    main()
