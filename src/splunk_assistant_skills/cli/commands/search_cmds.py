"""Search commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-search"


@click.group()
def search():
    """SPL query execution commands.

    Execute Splunk searches in various modes: oneshot, normal, or blocking.
    """
    pass


@search.command()
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--earliest", "-e", help="Earliest time (e.g., -1h, -24h@h).")
@click.option("--latest", "-l", help="Latest time (e.g., now, -1h).")
@click.option("--count", "-c", type=int, help="Maximum number of results.")
@click.option("--fields", "-f", help="Comma-separated list of fields to return.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format.",
)
@click.option("--output-file", help="Write results to file (for csv).")
@click.pass_context
def oneshot(ctx, spl, profile, earliest, latest, count, fields, output, output_file):
    """Execute a oneshot search (results returned inline).

    Best for ad-hoc queries with results under 50,000 rows.

    Example:
        splunk-skill search oneshot "index=main | stats count by sourcetype"
    """
    args = [spl]
    if profile:
        args.extend(["--profile", profile])
    if earliest:
        args.extend(["--earliest", earliest])
    if latest:
        args.extend(["--latest", latest])
    if count:
        args.extend(["--count", str(count)])
    if fields:
        args.extend(["--fields", fields])
    if output:
        args.extend(["--output", output])
    if output_file:
        args.extend(["--output-file", output_file])

    result = run_skill_script_subprocess(SKILL_NAME, "search_oneshot.py", args)
    ctx.exit(result.returncode)


@search.command()
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--earliest", "-e", help="Earliest time.")
@click.option("--latest", "-l", help="Latest time.")
@click.option("--wait/--no-wait", default=False, help="Wait for job completion.")
@click.option("--timeout", type=int, default=300, help="Timeout in seconds.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def normal(ctx, spl, profile, earliest, latest, wait, timeout, output):
    """Execute a normal (async) search.

    Returns a search ID (SID) immediately. Use 'job status' to check progress.

    Example:
        splunk-skill search normal "index=main | stats count" --wait
    """
    args = [spl]
    if profile:
        args.extend(["--profile", profile])
    if earliest:
        args.extend(["--earliest", earliest])
    if latest:
        args.extend(["--latest", latest])
    if wait:
        args.append("--wait")
    if timeout:
        args.extend(["--timeout", str(timeout)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "search_normal.py", args)
    ctx.exit(result.returncode)


@search.command()
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--earliest", "-e", help="Earliest time.")
@click.option("--latest", "-l", help="Latest time.")
@click.option("--timeout", type=int, default=300, help="Timeout in seconds.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def blocking(ctx, spl, profile, earliest, latest, timeout, output):
    """Execute a blocking search (waits for completion).

    Example:
        splunk-skill search blocking "index=main | head 10" --timeout 60
    """
    args = [spl]
    if profile:
        args.extend(["--profile", profile])
    if earliest:
        args.extend(["--earliest", earliest])
    if latest:
        args.extend(["--latest", latest])
    if timeout:
        args.extend(["--timeout", str(timeout)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "search_blocking.py", args)
    ctx.exit(result.returncode)


@search.command()
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--strict/--no-strict", default=False, help="Enable strict validation.")
@click.pass_context
def validate(ctx, spl, profile, strict):
    """Validate SPL syntax without executing.

    Example:
        splunk-skill search validate "index=main | stats count"
    """
    args = [spl]
    if profile:
        args.extend(["--profile", profile])
    if strict:
        args.append("--strict")

    result = run_skill_script_subprocess(SKILL_NAME, "validate_spl.py", args)
    ctx.exit(result.returncode)


@search.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--count", "-c", type=int, help="Maximum results to return.")
@click.option("--offset", type=int, default=0, help="Offset for pagination.")
@click.option("--fields", "-f", help="Comma-separated fields to return.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def results(ctx, sid, profile, count, offset, fields, output):
    """Get results from a completed search job.

    Example:
        splunk-skill search results 1703779200.12345 --count 100
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])
    if count:
        args.extend(["--count", str(count)])
    if offset:
        args.extend(["--offset", str(offset)])
    if fields:
        args.extend(["--fields", fields])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_results.py", args)
    ctx.exit(result.returncode)


@search.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--count", "-c", type=int, help="Maximum results to return.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def preview(ctx, sid, profile, count, output):
    """Get preview results from a running search job.

    Example:
        splunk-skill search preview 1703779200.12345
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])
    if count:
        args.extend(["--count", str(count)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_preview.py", args)
    ctx.exit(result.returncode)
