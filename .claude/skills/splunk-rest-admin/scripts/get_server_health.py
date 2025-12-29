#!/usr/bin/env python3
"""Get Splunk server health status."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))

from config_manager import get_splunk_client
from error_handler import handle_errors
from formatters import format_json, format_table, print_success


@handle_errors
def main():
    parser = argparse.ArgumentParser(description='Get server health')
    parser.add_argument('--profile', '-p', help='Splunk profile')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    response = client.get(
        '/services/server/health/splunkd',
        operation='get server health'
    )

    if args.output == 'json':
        print(format_json(response))
    else:
        entry = response.get('entry', [{}])[0]
        content = entry.get('content', {})

        # Extract health status
        health = content.get('health', 'unknown')
        features = content.get('features', {})

        details = [
            {'Component': 'Overall Health', 'Status': health.upper()},
        ]

        # Add feature health
        for feature_name, feature_data in features.items():
            if isinstance(feature_data, dict):
                feature_health = feature_data.get('health', 'unknown')
                details.append({
                    'Component': feature_name,
                    'Status': feature_health.upper(),
                })

        print(format_table(details))
        print_success(f"Server health: {health.upper()}")


if __name__ == '__main__':
    main()
