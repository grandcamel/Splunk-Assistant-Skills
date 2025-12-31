"""Saved search commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-savedsearch"


@click.group()
def savedsearch():
    """Saved search and report management.

    Create, run, and manage saved searches and scheduled reports.
    """
    pass


@savedsearch.command(name="list")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", help="Filter by app.")
@click.option("--owner", help="Filter by owner.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_savedsearches(ctx, profile, app, owner, output):
    """List all saved searches.

    Example:
        splunk-skill savedsearch list --app search
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if owner:
        args.extend(["--owner", owner])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_savedsearches.py", args)
    ctx.exit(result.returncode)


@savedsearch.command()
@click.argument("name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def get(ctx, name, profile, app, output):
    """Get details of a saved search.

    Example:
        splunk-skill savedsearch get "My Daily Report"
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_savedsearch.py", args)
    ctx.exit(result.returncode)


@savedsearch.command()
@click.argument("name")
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--description", "-d", help="Description of the saved search.")
@click.option("--cron", help="Cron schedule (e.g., '0 6 * * *').")
@click.option("--enabled/--disabled", default=True, help="Enable scheduling.")
@click.pass_context
def create(ctx, name, spl, profile, app, description, cron, enabled):
    """Create a new saved search.

    Example:
        splunk-skill savedsearch create "Daily Errors" "index=main level=ERROR | stats count"
    """
    args = [name, spl]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if description:
        args.extend(["--description", description])
    if cron:
        args.extend(["--cron", cron])
    if not enabled:
        args.append("--disabled")

    result = run_skill_script_subprocess(SKILL_NAME, "create_savedsearch.py", args)
    ctx.exit(result.returncode)


@savedsearch.command()
@click.argument("name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--spl", help="New SPL query.")
@click.option("--description", "-d", help="New description.")
@click.option("--cron", help="New cron schedule.")
@click.pass_context
def update(ctx, name, profile, app, spl, description, cron):
    """Update an existing saved search.

    Example:
        splunk-skill savedsearch update "Daily Errors" --cron "0 8 * * *"
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if spl:
        args.extend(["--spl", spl])
    if description:
        args.extend(["--description", description])
    if cron:
        args.extend(["--cron", cron])

    result = run_skill_script_subprocess(SKILL_NAME, "update_savedsearch.py", args)
    ctx.exit(result.returncode)


@savedsearch.command()
@click.argument("name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation.")
@click.pass_context
def delete(ctx, name, profile, app, force):
    """Delete a saved search.

    Example:
        splunk-skill savedsearch delete "Old Report" --force
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if force:
        args.append("--force")

    result = run_skill_script_subprocess(SKILL_NAME, "delete_savedsearch.py", args)
    ctx.exit(result.returncode)


@savedsearch.command()
@click.argument("name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--wait/--no-wait", default=True, help="Wait for completion.")
@click.option("--timeout", type=int, default=300, help="Timeout in seconds.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def run(ctx, name, profile, app, wait, timeout, output):
    """Run a saved search.

    Example:
        splunk-skill savedsearch run "Daily Errors" --wait
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if not wait:
        args.append("--no-wait")
    if timeout:
        args.extend(["--timeout", str(timeout)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "run_savedsearch.py", args)
    ctx.exit(result.returncode)


@savedsearch.command()
@click.argument("name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def enable(ctx, name, profile, app):
    """Enable scheduling for a saved search.

    Example:
        splunk-skill savedsearch enable "Daily Errors"
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "enable_schedule.py", args)
    ctx.exit(result.returncode)


@savedsearch.command()
@click.argument("name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def disable(ctx, name, profile, app):
    """Disable scheduling for a saved search.

    Example:
        splunk-skill savedsearch disable "Daily Errors"
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "disable_schedule.py", args)
    ctx.exit(result.returncode)
