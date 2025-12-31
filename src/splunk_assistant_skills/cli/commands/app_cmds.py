"""App management commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-app"


@click.group()
def app():
    """Application management.

    Install, configure, and manage Splunk applications.
    """
    pass


@app.command(name="list")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--filter", "-f", help="Filter apps by name pattern.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_apps(ctx, profile, filter, output):
    """List all installed apps.

    Example:
        splunk-skill app list
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if filter:
        args.extend(["--filter", filter])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_apps.py", args)
    ctx.exit(result.returncode)


@app.command()
@click.argument("app_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def get(ctx, app_name, profile, output):
    """Get details of an app.

    Example:
        splunk-skill app get search
    """
    args = [app_name]
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_app.py", args)
    ctx.exit(result.returncode)


@app.command()
@click.argument("app_path")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--name", "-n", help="App name (defaults to package name).")
@click.option("--update/--no-update", default=False, help="Update if exists.")
@click.pass_context
def install(ctx, app_path, profile, name, update):
    """Install an app from a package file.

    Example:
        splunk-skill app install /path/to/my_app.tgz
    """
    args = [app_path]
    if profile:
        args.extend(["--profile", profile])
    if name:
        args.extend(["--name", name])
    if update:
        args.append("--update")

    result = run_skill_script_subprocess(SKILL_NAME, "install_app.py", args)
    ctx.exit(result.returncode)


@app.command()
@click.argument("app_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation.")
@click.pass_context
def uninstall(ctx, app_name, profile, force):
    """Uninstall an app.

    Example:
        splunk-skill app uninstall my_app --force
    """
    args = [app_name]
    if profile:
        args.extend(["--profile", profile])
    if force:
        args.append("--force")

    result = run_skill_script_subprocess(SKILL_NAME, "uninstall_app.py", args)
    ctx.exit(result.returncode)


@app.command()
@click.argument("app_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def enable(ctx, app_name, profile):
    """Enable an app.

    Example:
        splunk-skill app enable my_app
    """
    args = [app_name]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "enable_app.py", args)
    ctx.exit(result.returncode)


@app.command()
@click.argument("app_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def disable(ctx, app_name, profile):
    """Disable an app.

    Example:
        splunk-skill app disable my_app
    """
    args = [app_name]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "disable_app.py", args)
    ctx.exit(result.returncode)
