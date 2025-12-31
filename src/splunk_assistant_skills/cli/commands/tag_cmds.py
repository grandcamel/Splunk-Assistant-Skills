"""Tag commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-tag"


@click.group()
def tag():
    """Knowledge object tagging.

    Add, remove, and search by tags on Splunk knowledge objects.
    """
    pass


@tag.command(name="list")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--field", "-f", help="Filter by field name.")
@click.option("--value", "-v", help="Filter by field value.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_tags(ctx, profile, field, value, output):
    """List all tags.

    Example:
        splunk-skill tag list --field host
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if field:
        args.extend(["--field", field])
    if value:
        args.extend(["--value", value])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_tags.py", args)
    ctx.exit(result.returncode)


@tag.command()
@click.argument("tag_name")
@click.argument("field")
@click.argument("value")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def add(ctx, tag_name, field, value, profile, app):
    """Add a tag to a field value.

    Example:
        splunk-skill tag add production host myserver.example.com
    """
    args = [tag_name, field, value]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "add_tag.py", args)
    ctx.exit(result.returncode)


@tag.command()
@click.argument("tag_name")
@click.argument("field")
@click.argument("value")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def remove(ctx, tag_name, field, value, profile, app):
    """Remove a tag from a field value.

    Example:
        splunk-skill tag remove production host myserver.example.com
    """
    args = [tag_name, field, value]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "remove_tag.py", args)
    ctx.exit(result.returncode)


@tag.command()
@click.argument("tag_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--earliest", "-e", default="-24h", help="Earliest time.")
@click.option("--latest", "-l", default="now", help="Latest time.")
@click.option("--count", "-c", type=int, default=100, help="Maximum results.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def search(ctx, tag_name, profile, earliest, latest, count, output):
    """Search events by tag.

    Example:
        splunk-skill tag search production --earliest -1h
    """
    args = [tag_name]
    if profile:
        args.extend(["--profile", profile])
    if earliest:
        args.extend(["--earliest", earliest])
    if latest:
        args.extend(["--latest", latest])
    if count:
        args.extend(["--count", str(count)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "search_by_tag.py", args)
    ctx.exit(result.returncode)
