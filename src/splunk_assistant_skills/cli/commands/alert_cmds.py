"""Alert commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-alert"


@click.group()
def alert():
    """Alert management and monitoring.

    Create, trigger, and manage Splunk alerts.
    """
    pass


@alert.command(name="list")
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
def list_alerts(ctx, profile, app, output):
    """List all alerts.

    Example:
        splunk-skill alert list --app search
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_alerts.py", args)
    ctx.exit(result.returncode)


@alert.command()
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
    """Get details of an alert.

    Example:
        splunk-skill alert get "Critical Errors Alert"
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_alert.py", args)
    ctx.exit(result.returncode)


@alert.command()
@click.argument("name")
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--description", "-d", help="Alert description.")
@click.option("--severity", type=click.Choice(["1", "2", "3", "4", "5"]), default="3", help="Alert severity.")
@click.option("--cron", help="Cron schedule.")
@click.pass_context
def create(ctx, name, spl, profile, app, description, severity, cron):
    """Create a new alert.

    Example:
        splunk-skill alert create "Error Alert" "index=main level=ERROR | stats count"
    """
    args = [name, spl]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if description:
        args.extend(["--description", description])
    if severity:
        args.extend(["--severity", severity])
    if cron:
        args.extend(["--cron", cron])

    result = run_skill_script_subprocess(SKILL_NAME, "create_alert.py", args)
    ctx.exit(result.returncode)


@alert.command()
@click.argument("name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--count", "-c", type=int, default=50, help="Maximum alerts to return.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def triggered(ctx, name, profile, app, count, output):
    """Get triggered alert instances.

    Example:
        splunk-skill alert triggered "Critical Errors Alert"
    """
    args = [name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if count:
        args.extend(["--count", str(count)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_triggered_alerts.py", args)
    ctx.exit(result.returncode)


@alert.command()
@click.argument("alert_id")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def acknowledge(ctx, alert_id, profile):
    """Acknowledge a triggered alert.

    Example:
        splunk-skill alert acknowledge 12345
    """
    args = [alert_id]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "acknowledge_alert.py", args)
    ctx.exit(result.returncode)
