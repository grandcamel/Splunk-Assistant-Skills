"""Lookup commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-lookup"


@click.group()
def lookup():
    """CSV and lookup file management.

    Upload, download, and manage lookup files in Splunk.
    """
    pass


@lookup.command(name="list")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", help="Filter by app.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_lookups(ctx, profile, app, output):
    """List all lookup files.

    Example:
        splunk-skill lookup list --app search
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_lookups.py", args)
    ctx.exit(result.returncode)


@lookup.command()
@click.argument("lookup_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def get(ctx, lookup_name, profile, app, output):
    """Get contents of a lookup file.

    Example:
        splunk-skill lookup get users.csv --app search
    """
    args = [lookup_name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_lookup.py", args)
    ctx.exit(result.returncode)


@lookup.command()
@click.argument("lookup_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--output-file", "-o", help="Output file path.")
@click.pass_context
def download(ctx, lookup_name, profile, app, output_file):
    """Download a lookup file.

    Example:
        splunk-skill lookup download users.csv -o users_backup.csv
    """
    args = [lookup_name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output_file:
        args.extend(["--output-file", output_file])

    result = run_skill_script_subprocess(SKILL_NAME, "download_lookup.py", args)
    ctx.exit(result.returncode)


@lookup.command()
@click.argument("file_path")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--name", "-n", help="Lookup name (defaults to filename).")
@click.pass_context
def upload(ctx, file_path, profile, app, name):
    """Upload a lookup file.

    Example:
        splunk-skill lookup upload /path/to/users.csv --app search
    """
    args = [file_path]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if name:
        args.extend(["--name", name])

    result = run_skill_script_subprocess(SKILL_NAME, "upload_lookup.py", args)
    ctx.exit(result.returncode)


@lookup.command()
@click.argument("lookup_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation.")
@click.pass_context
def delete(ctx, lookup_name, profile, app, force):
    """Delete a lookup file.

    Example:
        splunk-skill lookup delete old_users.csv --app search
    """
    args = [lookup_name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if force:
        args.append("--force")

    result = run_skill_script_subprocess(SKILL_NAME, "delete_lookup.py", args)
    ctx.exit(result.returncode)
