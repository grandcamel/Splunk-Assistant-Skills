#!/usr/bin/env python3
"""
Export Splunk search results to file.

Streams results efficiently for large exports (>50K rows).

Examples:
    python export_results.py "index=main | stats count by host" --output results.csv
    python export_results.py "index=main" --earliest -7d --format json --output data.json
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client, get_search_defaults, get_api_settings
from error_handler import handle_errors
from validators import validate_spl, validate_time_modifier
from formatters import print_success, print_info
from spl_helper import build_search
from job_poller import wait_for_job


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description='Export Splunk search results to file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('spl', help='SPL query to execute')
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'xml'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--profile', '-p', help='Splunk profile to use')
    parser.add_argument('--earliest', '-e', help='Earliest time')
    parser.add_argument('--latest', '-l', help='Latest time')
    parser.add_argument('--fields', help='Comma-separated fields to export')
    parser.add_argument('--progress', action='store_true', help='Show progress')
    args = parser.parse_args()

    # Get defaults
    defaults = get_search_defaults(args.profile)
    api_settings = get_api_settings(args.profile)
    earliest = args.earliest or defaults.get('earliest_time', '-24h')
    latest = args.latest or defaults.get('latest_time', 'now')

    # Validate
    spl = validate_spl(args.spl)
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    search_spl = build_search(spl, earliest_time=earliest, latest_time=latest)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Create job
    print_info("Creating search job...")
    response = client.post(
        '/search/v2/jobs',
        data={
            'search': search_spl,
            'exec_mode': 'normal',
            'earliest_time': earliest,
            'latest_time': latest,
        },
        operation='create export job',
    )

    sid = response.get('sid')
    if not sid and 'entry' in response:
        sid = response['entry'][0].get('name')

    # Wait for completion
    print_info(f"Waiting for job {sid}...")
    progress = wait_for_job(client, sid, timeout=api_settings.get('search_timeout', 300),
                           show_progress=args.progress)

    print_info(f"Exporting {progress.result_count:,} results...")

    # Build export params
    params = {
        'output_mode': args.format,
        'count': 0,  # All results
    }
    if args.fields:
        params['field_list'] = args.fields

    # Stream to file
    bytes_written = 0
    with open(args.output, 'wb') as f:
        for chunk in client.stream_results(
            f'/search/v2/jobs/{sid}/results',
            params=params,
            timeout=api_settings.get('search_timeout', 300),
            operation='export results',
        ):
            f.write(chunk)
            bytes_written += len(chunk)

    print_success(f"Exported {progress.result_count:,} results to {args.output}")
    print_info(f"File size: {bytes_written / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    main()
