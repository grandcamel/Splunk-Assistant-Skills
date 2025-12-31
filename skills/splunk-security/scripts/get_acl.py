#!/usr/bin/env python3
"""Get ACL (Access Control List) for a knowledge object."""

import argparse

from splunk_assistant_skills_lib import (
    format_json,
    format_table,
    get_splunk_client,
    handle_errors,
    print_success,
)


@handle_errors
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Get ACL (Access Control List) for a knowledge object",
        epilog="Examples:\n"
        "  python get_acl.py --object saved/searches/MySearch\n"
        "  python get_acl.py --object data/transforms/lookups/mylookup.csv\n"
        "  python get_acl.py --object data/indexes/main",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--object",
        "-obj",
        required=True,
        help="Object path (e.g., saved/searches/MySearch, data/indexes/main)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    client = get_splunk_client(profile=args.profile)

    # Build the ACL endpoint
    # Format: /services/{object}/acl
    acl_endpoint = f"/services/{args.object}/acl"

    response = client.get(
        acl_endpoint,
        params={"output_mode": "json"},
        operation=f"get ACL for {args.object}",
    )

    entry = response.get("entry", [{}])[0]
    content = entry.get("content", {})

    if args.output == "json":
        print(format_json(content))
    else:
        # Display basic ACL information
        perms = content.get("perms", {})
        read_perms = perms.get("read", [])
        write_perms = perms.get("write", [])

        basic_info = [
            {"Property": "Object", "Value": args.object},
            {"Property": "Owner", "Value": content.get("owner", "N/A")},
            {"Property": "App", "Value": content.get("app", "N/A")},
            {"Property": "Sharing", "Value": content.get("sharing", "N/A")},
            {"Property": "Modifiable", "Value": str(content.get("modifiable", "N/A"))},
            {"Property": "Removable", "Value": str(content.get("removable", "N/A"))},
        ]
        print("ACL Details:")
        print(format_table(basic_info))

        # Display read permissions
        if read_perms:
            print("\nRead Permissions:")
            read_data = [{"User/Role": perm} for perm in read_perms]
            print(format_table(read_data))
        else:
            print("\nRead Permissions: None")

        # Display write permissions
        if write_perms:
            print("\nWrite Permissions:")
            write_data = [{"User/Role": perm} for perm in write_perms]
            print(format_table(write_data))
        else:
            print("\nWrite Permissions: None")

        print_success(f"ACL retrieved for '{args.object}'")


if __name__ == "__main__":
    main()
