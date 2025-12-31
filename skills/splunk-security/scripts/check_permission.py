#!/usr/bin/env python3
"""Check if the current user has permission to access a resource."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_splunk_client,
    handle_errors,
    print_error,
    print_success,
)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Check permission to access a resource",
        epilog="Example: python check_permission.py --object saved/searches/MySearch --action read",
    )
    parser.add_argument(
        "--object",
        "-obj",
        required=True,
        help="Object path (e.g., saved/searches/MySearch, data/indexes/main)",
    )
    parser.add_argument(
        "--action",
        "-a",
        choices=["read", "write", "delete"],
        default="read",
        help="Action to check (default: read)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Get current user context first
    user_response = client.get(
        "/services/authentication/current-context",
        params={"output_mode": "json"},
        operation="get current user",
    )

    user_entry = user_response.get("entry", [{}])[0]
    user_content = user_entry.get("content", {})
    username = user_content.get("username", "N/A")
    capabilities = user_content.get("capabilities", [])

    # Try to get the ACL for the specific object
    try:
        # Build the ACL endpoint based on object path
        # Format: /services/{object}/acl
        acl_endpoint = f"/services/{args.object}/acl"

        acl_response = client.get(
            acl_endpoint,
            params={"output_mode": "json"},
            operation=f"get ACL for {args.object}",
        )

        acl_entry = acl_response.get("entry", [{}])[0]
        acl_content = acl_entry.get("content", {})
        perms = acl_content.get("perms", {})

        # Check permissions based on action
        has_permission = False
        permission_details = {}

        if args.action == "read":
            read_users = perms.get("read", [])
            read_roles = user_content.get("roles", [])
            has_permission = (
                username in read_users
                or any(role in read_users for role in read_roles)
                or "*" in read_users
            )
            permission_details["read_users"] = read_users
        elif args.action == "write":
            write_users = perms.get("write", [])
            write_roles = user_content.get("roles", [])
            has_permission = (
                username in write_users
                or any(role in write_roles for role in write_roles)
                or "*" in write_users
            )
            permission_details["write_users"] = write_users
        elif args.action == "delete":
            # Delete typically requires write permission
            write_users = perms.get("write", [])
            write_roles = user_content.get("roles", [])
            has_permission = (
                username in write_users
                or any(role in write_roles for role in write_roles)
                or "*" in write_users
            )
            permission_details["write_users"] = write_users

        owner = acl_content.get("owner", "N/A")
        sharing = acl_content.get("sharing", "N/A")

        if args.output == "json":
            result = {
                "username": username,
                "object": args.object,
                "action": args.action,
                "has_permission": has_permission,
                "owner": owner,
                "sharing": sharing,
                "permissions": permission_details,
            }
            print(format_json(result))
        else:
            details = [
                {"Property": "User", "Value": username},
                {"Property": "Object", "Value": args.object},
                {"Property": "Action", "Value": args.action},
                {
                    "Property": "Has Permission",
                    "Value": "Yes" if has_permission else "No",
                },
                {"Property": "Owner", "Value": owner},
                {"Property": "Sharing", "Value": sharing},
            ]
            print(format_table(details))

            if has_permission:
                print_success(
                    f"User '{username}' has '{args.action}' permission for '{args.object}'"
                )
            else:
                print_error(
                    f"User '{username}' does NOT have '{args.action}' permission for '{args.object}'"
                )

    except Exception as e:
        # If we can't get ACL, fall back to capability-based check
        if args.output == "json":
            result = {
                "username": username,
                "object": args.object,
                "action": args.action,
                "error": str(e),
                "capabilities": capabilities,
            }
            print(format_json(result))
        else:
            print_error(f"Could not retrieve ACL for '{args.object}': {e}")
            print(f"\nUser capabilities ({len(capabilities)}):")
            if capabilities:
                cap_data = [{"Capability": cap} for cap in sorted(capabilities)[:20]]
                print(format_table(cap_data))
                if len(capabilities) > 20:
                    print(f"... and {len(capabilities) - 20} more")


if __name__ == "__main__":
    main()
