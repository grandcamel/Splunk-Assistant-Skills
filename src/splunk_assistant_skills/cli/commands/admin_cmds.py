"""Admin commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-rest-admin"


@click.group()
def admin():
    """Server administration and REST API access.

    Check server status, health, and make generic REST calls.
    """
    pass


@admin.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def info(ctx, profile, output):
    """Get server information.

    Example:
        splunk-skill admin info
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_server_info.py", args)
    ctx.exit(result.returncode)


@admin.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def status(ctx, profile, output):
    """Get server status.

    Example:
        splunk-skill admin status
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_server_status.py", args)
    ctx.exit(result.returncode)


@admin.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def health(ctx, profile, output):
    """Get server health status.

    Example:
        splunk-skill admin health
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_server_health.py", args)
    ctx.exit(result.returncode)


@admin.command(name="list-users")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_users(ctx, profile, output):
    """List all users.

    Example:
        splunk-skill admin list-users
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_users.py", args)
    ctx.exit(result.returncode)


@admin.command(name="list-roles")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_roles(ctx, profile, output):
    """List all roles.

    Example:
        splunk-skill admin list-roles
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_roles.py", args)
    ctx.exit(result.returncode)


@admin.command()
@click.argument("endpoint")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", help="App context.")
@click.option("--owner", help="Owner context.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="json",
    help="Output format.",
)
@click.pass_context
def rest_get(ctx, endpoint, profile, app, owner, output):
    """Make a GET request to a REST endpoint.

    Example:
        splunk-skill admin rest-get /services/server/info
    """
    args = [endpoint]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if owner:
        args.extend(["--owner", owner])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "rest_get.py", args)
    ctx.exit(result.returncode)


@admin.command()
@click.argument("endpoint")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--data", "-d", help="POST data (JSON or key=value pairs).")
@click.option("--app", "-a", help="App context.")
@click.option("--owner", help="Owner context.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="json",
    help="Output format.",
)
@click.pass_context
def rest_post(ctx, endpoint, profile, data, app, owner, output):
    """Make a POST request to a REST endpoint.

    Example:
        splunk-skill admin rest-post /services/saved/searches -d '{"name": "test"}'
    """
    args = [endpoint]
    if profile:
        args.extend(["--profile", profile])
    if data:
        args.extend(["--data", data])
    if app:
        args.extend(["--app", app])
    if owner:
        args.extend(["--owner", owner])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "rest_post.py", args)
    ctx.exit(result.returncode)
