#!/usr/bin/env python3
"""List sourcetypes in Splunk."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, format_table, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description='List sourcetypes')
    parser.add_argument('--index', '-i', help='Filter by index')
    parser.add_argument('--count', '-c', type=int, default=100, help='Max results (default: 100)')
    parser.add_argument('--profile', '-p', help='Splunk profile')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Use metadata search to get sourcetypes
    search = '| metadata type=sourcetypes'
    if args.index:
        search += f' index={args.index}'
    search += ' | sort -totalCount | head ' + str(args.count)

    response = client.post(
        '/search/jobs/oneshot',
        data={
            'search': search,
            'output_mode': 'json',
            'earliest_time': '-24h',
            'latest_time': 'now',
        },
        operation='list sourcetypes'
    )

    results = response.get('results', [])

    if args.output == 'json':
        print(format_json(results))
    else:
        display_data = [{
            'Sourcetype': r.get('sourcetype', 'N/A'),
            'Total Count': r.get('totalCount', 0),
            'First Time': r.get('firstTime', 'N/A')[:19] if r.get('firstTime') else 'N/A',
            'Last Time': r.get('lastTime', 'N/A')[:19] if r.get('lastTime') else 'N/A',
        } for r in results]
        print(format_table(display_data))
        index_info = f" in index '{args.index}'" if args.index else ""
        print_success(f"Found {len(results)} sourcetypes{index_info}")


if __name__ == '__main__':
    main()
