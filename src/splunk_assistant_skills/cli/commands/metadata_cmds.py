"""Metadata commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-metadata"


@click.group()
def metadata():
    """Index, source, and sourcetype discovery.

    Explore and discover metadata about your Splunk environment.
    """
    pass


@metadata.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--filter", "-f", help="Filter indexes by name pattern.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def indexes(ctx, profile, filter, output):
    """List all indexes.

    Example:
        splunk-skill metadata indexes
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if filter:
        args.extend(["--filter", filter])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_indexes.py", args)
    ctx.exit(result.returncode)


@metadata.command()
@click.argument("index_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def index_info(ctx, index_name, profile, output):
    """Get detailed information about an index.

    Example:
        splunk-skill metadata index-info main
    """
    args = [index_name]
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_index_info.py", args)
    ctx.exit(result.returncode)


@metadata.command()
@click.argument("index_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def create_index(ctx, index_name, profile):
    """Create a new index.

    Example:
        splunk-skill metadata create-index my_new_index
    """
    args = [index_name]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "create_index.py", args)
    ctx.exit(result.returncode)


@metadata.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--index", "-i", help="Filter by index.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def sourcetypes(ctx, profile, index, output):
    """List all sourcetypes.

    Example:
        splunk-skill metadata sourcetypes --index main
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if index:
        args.extend(["--index", index])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_sourcetypes.py", args)
    ctx.exit(result.returncode)


@metadata.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--index", "-i", help="Filter by index.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def sources(ctx, profile, index, output):
    """List all sources.

    Example:
        splunk-skill metadata sources --index main
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if index:
        args.extend(["--index", index])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_sources.py", args)
    ctx.exit(result.returncode)


@metadata.command()
@click.argument("index_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--sourcetype", "-s", help="Filter by sourcetype.")
@click.option("--earliest", "-e", default="-24h", help="Earliest time.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def fields(ctx, index_name, profile, sourcetype, earliest, output):
    """Get field summary for an index.

    Example:
        splunk-skill metadata fields main --sourcetype access_combined
    """
    args = [index_name]
    if profile:
        args.extend(["--profile", profile])
    if sourcetype:
        args.extend(["--sourcetype", sourcetype])
    if earliest:
        args.extend(["--earliest", earliest])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_field_summary.py", args)
    ctx.exit(result.returncode)


@metadata.command()
@click.argument("metadata_type", type=click.Choice(["hosts", "sources", "sourcetypes"]))
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--index", "-i", help="Filter by index.")
@click.option("--earliest", "-e", default="-24h", help="Earliest time.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def search(ctx, metadata_type, profile, index, earliest, output):
    """Search metadata using the metadata command.

    Example:
        splunk-skill metadata search sourcetypes --index main
    """
    args = [metadata_type]
    if profile:
        args.extend(["--profile", profile])
    if index:
        args.extend(["--index", index])
    if earliest:
        args.extend(["--earliest", earliest])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "metadata_search.py", args)
    ctx.exit(result.returncode)
