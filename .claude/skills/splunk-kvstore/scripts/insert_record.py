#!/usr/bin/env python3
"""Insert a record into a KV Store collection."""

import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import print_success, format_json


@handle_errors
def main():
    parser = argparse.ArgumentParser(description='Insert record into KV Store collection')
    parser.add_argument('collection', help='Collection name')
    parser.add_argument('data', help='Record data as JSON: {"field1": "value1", "field2": 123}')
    parser.add_argument('--app', '-a', default='search', help='App namespace (default: search)')
    parser.add_argument('--key', '-k', help='Specify _key value (auto-generated if not provided)')
    parser.add_argument('--profile', '-p', help='Splunk profile')
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    record = json.loads(args.data)
    if args.key:
        record['_key'] = args.key

    response = client.post(
        f'/servicesNS/nobody/{args.app}/storage/collections/data/{args.collection}',
        json_body=record,
        operation='insert record'
    )

    # Response contains the _key of the inserted record
    key = response.get('_key', 'unknown')
    print_success(f"Record inserted with _key: {key}")
    print(format_json(response))


if __name__ == '__main__':
    main()
