#!/usr/bin/env python3
"""Get details of a Splunk index."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, format_table, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description='Get index details')
    parser.add_argument('name', help='Index name')
    parser.add_argument('--profile', '-p', help='Splunk profile')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        f'/data/indexes/{args.name}',
        operation='get index'
    )

    if args.output == 'json':
        print(format_json(response))
    else:
        entry = response.get('entry', [{}])[0]
        content = entry.get('content', {})

        details = [
            {'Property': 'Name', 'Value': entry.get('name', 'N/A')},
            {'Property': 'Datatype', 'Value': content.get('datatype', 'event')},
            {'Property': 'Home Path', 'Value': content.get('homePath', 'N/A')},
            {'Property': 'Cold Path', 'Value': content.get('coldPath', 'N/A')},
            {'Property': 'Thawed Path', 'Value': content.get('thawedPath', 'N/A')},
            {'Property': 'Max Data Size', 'Value': content.get('maxDataSize', 'N/A')},
            {'Property': 'Max Total Size (MB)', 'Value': content.get('maxTotalDataSizeMB', 'N/A')},
            {'Property': 'Frozen Time (sec)', 'Value': content.get('frozenTimePeriodInSecs', 'N/A')},
            {'Property': 'Total Event Count', 'Value': content.get('totalEventCount', 'N/A')},
            {'Property': 'Current Size (MB)', 'Value': content.get('currentDBSizeMB', 'N/A')},
            {'Property': 'Disabled', 'Value': 'Yes' if content.get('disabled') else 'No'},
        ]
        print(format_table(details))
        print_success(f"Retrieved index: {args.name}")


if __name__ == '__main__':
    main()
