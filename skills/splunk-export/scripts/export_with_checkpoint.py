#!/usr/bin/env python3
"""
Export Splunk search results with checkpoint-based resume capability.

Enables reliable exports of very large result sets by saving progress periodically.
If interrupted, the export can be resumed from the last checkpoint.

Examples:
    # Start new export with checkpoint
    python export_with_checkpoint.py "index=main | stats count by host" \
        --output results.csv --checkpoint export.ckpt

    # Resume interrupted export
    python export_with_checkpoint.py --resume export.ckpt

    # Custom chunk size (rows per checkpoint)
    python export_with_checkpoint.py "index=main" \
        --output data.csv --checkpoint export.ckpt --chunk-size 10000
"""

import argparse
import json
import os

from splunk_assistant_skills_lib import (
    build_search,
    get_api_settings,
    get_search_defaults,
    get_splunk_client,
    handle_errors,
    print_error,
    print_info,
    print_success,
    validate_spl,
    validate_time_modifier,
    wait_for_job,
)


def save_checkpoint(checkpoint_file, data):
    """Save checkpoint data to file."""
    with open(checkpoint_file, "w") as f:
        json.dump(data, f, indent=2)


def load_checkpoint(checkpoint_file):
    """Load checkpoint data from file."""
    if not os.path.exists(checkpoint_file):
        return None
    with open(checkpoint_file, "r") as f:
        return json.load(f)


@handle_errors
def main():
    parser = argparse.ArgumentParser(
        description="Export with checkpoint-based resume capability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("spl", nargs="?", help="SPL query to execute")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument(
        "--checkpoint", "-c", required=True, help="Checkpoint file path"
    )
    parser.add_argument(
        "--resume", "-r", action="store_true", help="Resume from checkpoint"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["csv", "json", "xml"],
        default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=50000,
        help="Rows per checkpoint (default: 50000)",
    )
    parser.add_argument("--profile", "-p", help="Splunk profile to use")
    parser.add_argument("--earliest", "-e", help="Earliest time")
    parser.add_argument("--latest", "-l", help="Latest time")
    parser.add_argument("--fields", help="Comma-separated fields to export")
    parser.add_argument("--progress", action="store_true", help="Show progress")
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)

    # Resume mode
    if args.resume:
        checkpoint = load_checkpoint(args.checkpoint)
        if not checkpoint:
            print_error(f"Checkpoint file not found: {args.checkpoint}")
            return

        print_info(f"Resuming export from checkpoint...")
        print_info(f"  SID: {checkpoint['sid']}")
        print_info(f"  Offset: {checkpoint['offset']:,}")
        print_info(f"  Total results: {checkpoint['total_results']:,}")

        sid = checkpoint["sid"]
        offset = checkpoint["offset"]
        output_file = checkpoint["output_file"]
        output_format = checkpoint["format"]
        chunk_size = checkpoint["chunk_size"]
        total_results = checkpoint["total_results"]
        fields = checkpoint.get("fields")

    # New export mode
    else:
        if not args.spl or not args.output:
            print_error("--spl and --output required for new export")
            return

        # Get defaults
        defaults = get_search_defaults(args.profile)
        api_settings = get_api_settings(args.profile)
        earliest = args.earliest or defaults.get("earliest_time", "-24h")
        latest = args.latest or defaults.get("latest_time", "now")

        # Validate
        spl = validate_spl(args.spl)
        earliest = validate_time_modifier(earliest)
        latest = validate_time_modifier(latest)

        search_spl = build_search(spl, earliest_time=earliest, latest_time=latest)

        # Create job
        print_info("Creating search job...")
        response = client.post(
            "/search/v2/jobs",
            data={
                "search": search_spl,
                "exec_mode": "normal",
                "earliest_time": earliest,
                "latest_time": latest,
            },
            operation="create export job",
        )

        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        # Wait for completion
        print_info(f"Waiting for job {sid}...")
        progress = wait_for_job(
            client,
            sid,
            timeout=api_settings.get("search_timeout", 300),
            show_progress=args.progress,
        )

        total_results = progress.result_count
        offset = 0
        output_file = args.output
        output_format = args.format
        chunk_size = args.chunk_size
        fields = args.fields

        print_info(f"Starting export of {total_results:,} results...")

        # Save initial checkpoint
        checkpoint_data = {
            "sid": sid,
            "offset": 0,
            "total_results": total_results,
            "output_file": output_file,
            "format": output_format,
            "chunk_size": chunk_size,
            "fields": fields,
        }
        save_checkpoint(args.checkpoint, checkpoint_data)

    # Open output file (append mode for resume)
    file_mode = "ab" if args.resume else "wb"
    api_settings = get_api_settings(args.profile)

    with open(output_file, file_mode) as f:
        bytes_written = 0

        # Export in chunks
        while offset < total_results:
            rows_remaining = total_results - offset
            current_chunk = min(chunk_size, rows_remaining)

            print_info(
                f"Exporting rows {offset:,} to {offset + current_chunk:,} "
                f"of {total_results:,} ({offset * 100 // total_results}%)"
            )

            # Build export params
            params = {
                "output_mode": output_format,
                "offset": offset,
                "count": current_chunk,
            }
            if fields:
                params["field_list"] = fields

            # Stream chunk to file
            chunk_bytes = 0
            for chunk in client.stream_results(
                f"/search/v2/jobs/{sid}/results",
                params=params,
                timeout=api_settings.get("search_timeout", 300),
                operation="export results chunk",
            ):
                f.write(chunk)
                chunk_bytes += len(chunk)

            bytes_written += chunk_bytes
            offset += current_chunk

            # Update checkpoint
            checkpoint_data = {
                "sid": sid,
                "offset": offset,
                "total_results": total_results,
                "output_file": output_file,
                "format": output_format,
                "chunk_size": chunk_size,
                "fields": fields,
            }
            save_checkpoint(args.checkpoint, checkpoint_data)

    # Clean up checkpoint on successful completion
    if offset >= total_results:
        os.remove(args.checkpoint)
        print_success(f"Export completed: {total_results:,} results to {output_file}")
        print_info(f"File size: {bytes_written / 1024 / 1024:.2f} MB")
        print_info(f"Checkpoint removed: {args.checkpoint}")
    else:
        print_info(f"Export paused at offset {offset:,}")
        print_info(
            f"Resume with: python export_with_checkpoint.py --resume {args.checkpoint}"
        )


if __name__ == "__main__":
    main()
