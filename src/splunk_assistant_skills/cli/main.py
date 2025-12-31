"""Splunk Assistant Skills CLI - Main entry point."""

import click

from splunk_assistant_skills import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="splunk-skill")
@click.option(
    "--profile",
    "-p",
    envvar="SPLUNK_PROFILE",
    help="Splunk profile to use for authentication.",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output.",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress non-essential output.",
)
@click.pass_context
def cli(ctx, profile, output, verbose, quiet):
    """Splunk Assistant Skills CLI.

    A command-line interface for interacting with Splunk through
    various skill-based commands.

    Use --help on any command for more information.

    Examples:

        splunk-skill search oneshot "index=main | head 10"

        splunk-skill job status abc123

        splunk-skill metadata indexes
    """
    # Ensure ctx.obj exists for storing global options
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["output"] = output
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet

    # Show help if no subcommand provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Import and register command groups
# These imports are done here to avoid circular imports
def register_commands():
    """Register all command groups with the CLI."""
    from .commands.search_cmds import search
    from .commands.job_cmds import job
    from .commands.export_cmds import export
    from .commands.metadata_cmds import metadata
    from .commands.lookup_cmds import lookup
    from .commands.kvstore_cmds import kvstore
    from .commands.savedsearch_cmds import savedsearch
    from .commands.alert_cmds import alert
    from .commands.app_cmds import app
    from .commands.security_cmds import security
    from .commands.admin_cmds import admin
    from .commands.tag_cmds import tag
    from .commands.metrics_cmds import metrics

    cli.add_command(search)
    cli.add_command(job)
    cli.add_command(export)
    cli.add_command(metadata)
    cli.add_command(lookup)
    cli.add_command(kvstore)
    cli.add_command(savedsearch)
    cli.add_command(alert)
    cli.add_command(app)
    cli.add_command(security)
    cli.add_command(admin)
    cli.add_command(tag)
    cli.add_command(metrics)


# Register commands when module is loaded
register_commands()


if __name__ == "__main__":
    cli()
