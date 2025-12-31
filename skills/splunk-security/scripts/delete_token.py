#!/usr/bin/env python3
"""Delete (revoke) a JWT authentication token."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_error,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Delete (revoke) a JWT authentication token"
    )
    parser.add_argument(
        "token_id",
        help="Token ID to delete",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    # Confirm deletion unless --force is used
    if not args.force:
        confirm = input(f"Delete token '{args.token_id}'? (y/N): ")
        if confirm.lower() != "y":
            print_error("Deletion cancelled")
            return

    # Delete the token
    client.delete(
        f"/services/authorization/tokens/{args.token_id}",
        operation="delete token",
    )

    print_success(f"Token '{args.token_id}' deleted successfully")


if __name__ == "__main__":
    main()
