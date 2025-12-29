#!/usr/bin/env python3
"""
Cancel a running Splunk search job.

Issues the cancel control action to stop a running search.

Examples:
    python cancel_job.py 1703779200.12345
"""

import sys
import argparse
from pathlib import Path

# Add shared lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from validators import validate_sid
from formatters import print_success
from job_poller import cancel_job


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description='Cancel a Splunk search job',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('sid', help='Search job ID')
    parser.add_argument('--profile', '-p', help='Splunk profile to use')
    args = parser.parse_args()

    # Validate SID
    sid = validate_sid(args.sid)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Cancel job
    cancel_job(client, sid)
    print_success(f"Job cancelled: {sid}")


if __name__ == '__main__':
    main()
