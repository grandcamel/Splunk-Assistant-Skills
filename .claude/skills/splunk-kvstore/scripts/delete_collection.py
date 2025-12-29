#!/usr/bin/env python3
"""Delete a KV Store collection."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import print_success, print_warning


@handle_errors
def main():
    parser = argparse.ArgumentParser(description='Delete KV Store collection')
    parser.add_argument('name', help='Collection name')
    parser.add_argument('--app', '-a', default='search', help='App namespace (default: search)')
    parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
    parser.add_argument('--profile', '-p', help='Splunk profile')
    args = parser.parse_args()

    if not args.force:
        print_warning(f"This will permanently delete collection '{args.name}' and all its data.")
        confirm = input("Type 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            print("Cancelled.")
            return

    client = get_splunk_client(profile=args.profile)
    client.delete(
        f'/servicesNS/nobody/{args.app}/storage/collections/config/{args.name}',
        operation='delete collection'
    )

    print_success(f"Collection '{args.name}' deleted from app '{args.app}'")


if __name__ == '__main__':
    main()
