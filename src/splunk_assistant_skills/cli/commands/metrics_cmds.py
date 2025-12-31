"""Metrics commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-metrics"


@click.group()
def metrics():
    """Real-time metrics operations.

    Query metrics using mstats and mcatalog commands.
    """
    pass


@metrics.command(name="list")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--index", "-i", help="Filter by metrics index.")
@click.option("--filter", "-f", help="Filter by metric name pattern.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_metrics(ctx, profile, index, filter, output):
    """List available metrics.

    Example:
        splunk-skill metrics list --index my_metrics
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if index:
        args.extend(["--index", index])
    if filter:
        args.extend(["--filter", filter])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_metrics.py", args)
    ctx.exit(result.returncode)


@metrics.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def indexes(ctx, profile, output):
    """List metrics indexes.

    Example:
        splunk-skill metrics indexes
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_metric_indexes.py", args)
    ctx.exit(result.returncode)


@metrics.command()
@click.argument("metric_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--index", "-i", default="metrics", help="Metrics index.")
@click.option("--span", "-s", default="1h", help="Time span for aggregation.")
@click.option("--earliest", "-e", default="-24h", help="Earliest time.")
@click.option("--latest", "-l", default="now", help="Latest time.")
@click.option("--agg", type=click.Choice(["avg", "sum", "min", "max", "count"]), default="avg", help="Aggregation function.")
@click.option("--by", help="Split by dimension.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def mstats(ctx, metric_name, profile, index, span, earliest, latest, agg, by, output):
    """Query metrics using mstats.

    Example:
        splunk-skill metrics mstats cpu.percent --span 5m --by host
    """
    args = [metric_name]
    if profile:
        args.extend(["--profile", profile])
    if index:
        args.extend(["--index", index])
    if span:
        args.extend(["--span", span])
    if earliest:
        args.extend(["--earliest", earliest])
    if latest:
        args.extend(["--latest", latest])
    if agg:
        args.extend(["--agg", agg])
    if by:
        args.extend(["--by", by])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "mstats.py", args)
    ctx.exit(result.returncode)


@metrics.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--index", "-i", default="metrics", help="Metrics index.")
@click.option("--filter", "-f", help="Filter by metric name pattern.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def mcatalog(ctx, profile, index, filter, output):
    """Discover metrics metadata using mcatalog.

    Example:
        splunk-skill metrics mcatalog --index my_metrics --filter "cpu.*"
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if index:
        args.extend(["--index", index])
    if filter:
        args.extend(["--filter", filter])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "mcatalog.py", args)
    ctx.exit(result.returncode)
