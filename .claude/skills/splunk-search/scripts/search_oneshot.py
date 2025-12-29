#!/usr/bin/env python3
"""
Execute a Splunk oneshot search.

Oneshot searches return results inline without creating a persistent job.
Best for ad-hoc queries with results under 50,000 rows.

Examples:
    python search_oneshot.py "index=main | stats count by sourcetype"
    python search_oneshot.py "index=main | head 100" --earliest -1h
    python search_oneshot.py "index=main | top host" --output json
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client, get_search_defaults, get_api_settings
from error_handler import handle_errors
from validators import validate_spl, validate_time_modifier
from formatters import print_success, format_search_results, format_json, export_csv
from spl_helper import build_search


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description='Execute a Splunk oneshot search',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python search_oneshot.py "index=main | stats count"
  python search_oneshot.py "index=main | head 100" --earliest -1h
  python search_oneshot.py "index=main | top host" --output json
        '''
    )
    parser.add_argument('spl', help='SPL query to execute')
    parser.add_argument('--profile', '-p', help='Splunk profile to use')
    parser.add_argument('--earliest', '-e', help='Earliest time')
    parser.add_argument('--latest', '-l', help='Latest time')
    parser.add_argument('--count', '-c', type=int, help='Maximum results')
    parser.add_argument('--fields', '-f', help='Comma-separated fields to return')
    parser.add_argument('--output', '-o', choices=['text', 'json', 'csv'], default='text',
                       help='Output format')
    parser.add_argument('--output-file', help='Write results to file (for csv)')
    args = parser.parse_args()

    # Get defaults
    defaults = get_search_defaults(args.profile)
    api_settings = get_api_settings(args.profile)

    earliest = args.earliest or defaults.get('earliest_time', '-24h')
    latest = args.latest or defaults.get('latest_time', 'now')
    max_count = args.count or defaults.get('max_count', 50000)

    # Validate inputs
    spl = validate_spl(args.spl)
    earliest = validate_time_modifier(earliest)
    latest = validate_time_modifier(latest)

    # Build search
    fields = args.fields.split(',') if args.fields else None
    search_spl = build_search(spl, earliest_time=earliest, latest_time=latest, fields=fields)

    # Get client
    client = get_splunk_client(profile=args.profile)

    # Execute oneshot search
    response = client.post(
        '/search/jobs/oneshot',
        data={
            'search': search_spl,
            'earliest_time': earliest,
            'latest_time': latest,
            'count': max_count,
            'output_mode': 'json',
        },
        timeout=api_settings.get('search_timeout', 300),
        operation='oneshot search',
    )

    # Extract results
    results = response.get('results', [])

    # Output
    if args.output == 'json':
        print(format_json(results))
    elif args.output == 'csv':
        if args.output_file:
            export_csv(results, args.output_file, columns=fields)
            print_success(f"Results written to {args.output_file}")
        else:
            print(format_search_results(results, fields=fields, output_format='csv'))
    else:
        print(format_search_results(results, fields=fields))
        print_success(f"Found {len(results)} results")


if __name__ == '__main__':
    main()
