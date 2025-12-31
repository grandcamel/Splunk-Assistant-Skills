"""Job management commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-job"


@click.group()
def job():
    """Search job lifecycle management.

    Create, monitor, control, and clean up Splunk search jobs.
    """
    pass


@job.command()
@click.argument("spl")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--earliest", "-e", help="Earliest time.")
@click.option("--latest", "-l", help="Latest time.")
@click.option(
    "--exec-mode",
    type=click.Choice(["normal", "blocking"]),
    default="normal",
    help="Execution mode.",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def create(ctx, spl, profile, earliest, latest, exec_mode, output):
    """Create a new search job.

    Example:
        splunk-skill job create "index=main | stats count"
    """
    args = [spl]
    if profile:
        args.extend(["--profile", profile])
    if earliest:
        args.extend(["--earliest", earliest])
    if latest:
        args.extend(["--latest", latest])
    if exec_mode:
        args.extend(["--exec-mode", exec_mode])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "create_job.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def status(ctx, sid, profile, output):
    """Get the status of a search job.

    Example:
        splunk-skill job status 1703779200.12345
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_job_status.py", args)
    ctx.exit(result.returncode)


@job.command(name="list")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--count", "-c", type=int, default=50, help="Maximum jobs to list.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_jobs(ctx, profile, count, output):
    """List search jobs.

    Example:
        splunk-skill job list --count 10
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if count:
        args.extend(["--count", str(count)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_jobs.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--timeout", type=int, default=300, help="Timeout in seconds.")
@click.option("--interval", type=float, default=2.0, help="Poll interval in seconds.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def poll(ctx, sid, profile, timeout, interval, output):
    """Poll a job until completion.

    Example:
        splunk-skill job poll 1703779200.12345 --timeout 60
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])
    if timeout:
        args.extend(["--timeout", str(timeout)])
    if interval:
        args.extend(["--interval", str(interval)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "poll_job.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def cancel(ctx, sid, profile):
    """Cancel a running search job.

    Example:
        splunk-skill job cancel 1703779200.12345
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "cancel_job.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def pause(ctx, sid, profile):
    """Pause a running search job.

    Example:
        splunk-skill job pause 1703779200.12345
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "pause_job.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def unpause(ctx, sid, profile):
    """Resume a paused search job.

    Example:
        splunk-skill job unpause 1703779200.12345
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "unpause_job.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def finalize(ctx, sid, profile):
    """Finalize a search job (stop and return current results).

    Example:
        splunk-skill job finalize 1703779200.12345
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "finalize_job.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def delete(ctx, sid, profile):
    """Delete a search job.

    Example:
        splunk-skill job delete 1703779200.12345
    """
    args = [sid]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "delete_job.py", args)
    ctx.exit(result.returncode)


@job.command()
@click.argument("sid")
@click.argument("ttl", type=int)
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def ttl(ctx, sid, ttl, profile):
    """Set the TTL (time-to-live) for a search job.

    Example:
        splunk-skill job ttl 1703779200.12345 3600
    """
    args = [sid, str(ttl)]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "set_job_ttl.py", args)
    ctx.exit(result.returncode)
