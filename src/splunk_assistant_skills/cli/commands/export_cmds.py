"""Export commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-export"


@click.group()
def export():
    """Data export and extraction commands.

    Export search results in various formats for ETL and analysis.
    """
    pass


@export.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--output-file", "-o", required=True, help="Output file path.")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xml"]),
    default="csv",
    help="Export format.",
)
@click.option("--count", "-c", type=int, help="Maximum results to export.")
@click.pass_context
def results(ctx, sid, profile, output_file, format, count):
    """Export results from a completed search job.

    Example:
        splunk-skill export results 1703779200.12345 -o results.csv
    """
    args = [sid, "--output-file", output_file]
    if profile:
        args.extend(["--profile", profile])
    if format:
        args.extend(["--format", format])
    if count:
        args.extend(["--count", str(count)])

    result = run_skill_script_subprocess(SKILL_NAME, "export_results.py", args)
    ctx.exit(result.returncode)


@export.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--output-file", "-o", required=True, help="Output file path.")
@click.pass_context
def raw(ctx, sid, profile, output_file):
    """Export raw events from a search job.

    Example:
        splunk-skill export raw 1703779200.12345 -o events.txt
    """
    args = [sid, "--output-file", output_file]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "export_raw.py", args)
    ctx.exit(result.returncode)


@export.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--output-file", "-o", required=True, help="Output file path.")
@click.option("--checkpoint-file", help="Checkpoint file for resumable exports.")
@click.option("--batch-size", type=int, default=10000, help="Batch size for export.")
@click.pass_context
def checkpoint(ctx, sid, profile, output_file, checkpoint_file, batch_size):
    """Export with checkpoint support for large datasets.

    Example:
        splunk-skill export checkpoint 1703779200.12345 -o large_export.csv
    """
    args = [sid, "--output-file", output_file]
    if profile:
        args.extend(["--profile", profile])
    if checkpoint_file:
        args.extend(["--checkpoint-file", checkpoint_file])
    if batch_size:
        args.extend(["--batch-size", str(batch_size)])

    result = run_skill_script_subprocess(SKILL_NAME, "export_with_checkpoint.py", args)
    ctx.exit(result.returncode)


@export.command()
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--earliest", "-e", help="Earliest time.")
@click.option("--latest", "-l", help="Latest time.")
@click.pass_context
def estimate(ctx, spl, profile, earliest, latest):
    """Estimate the size of an export before running it.

    Example:
        splunk-skill export estimate "index=main | head 10000"
    """
    args = [spl]
    if profile:
        args.extend(["--profile", profile])
    if earliest:
        args.extend(["--earliest", earliest])
    if latest:
        args.extend(["--latest", latest])

    result = run_skill_script_subprocess(SKILL_NAME, "estimate_export_size.py", args)
    ctx.exit(result.returncode)
