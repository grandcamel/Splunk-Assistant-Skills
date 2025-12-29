#!/usr/bin/env python3
"""Finalize a Splunk search job (stop streaming, return current results)."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from validators import validate_sid
from formatters import print_success
from job_poller import finalize_job


@handle_errors
def main():
    parser = argparse.ArgumentParser(description='Finalize a Splunk search job')
    parser.add_argument('sid', help='Search job ID')
    parser.add_argument('--profile', '-p', help='Splunk profile to use')
    args = parser.parse_args()

    sid = validate_sid(args.sid)
    client = get_splunk_client(profile=args.profile)
    finalize_job(client, sid)
    print_success(f"Job finalized: {sid}")


if __name__ == '__main__':
    main()
