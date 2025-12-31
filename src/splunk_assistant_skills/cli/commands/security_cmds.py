"""Security commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-security"


@click.group()
def security():
    """Token management and RBAC.

    Manage authentication tokens, users, and permissions.
    """
    pass


@security.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def whoami(ctx, profile, output):
    """Get current user information.

    Example:
        splunk-skill security whoami
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_current_user.py", args)
    ctx.exit(result.returncode)


@security.command(name="list-tokens")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def list_tokens(ctx, profile, output):
    """List authentication tokens.

    Example:
        splunk-skill security list-tokens
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_tokens.py", args)
    ctx.exit(result.returncode)


@security.command(name="create-token")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--name", "-n", required=True, help="Token name.")
@click.option("--audience", help="Token audience.")
@click.option("--expires", type=int, help="Expiration time in seconds.")
@click.pass_context
def create_token(ctx, profile, name, audience, expires):
    """Create a new authentication token.

    Example:
        splunk-skill security create-token --name "API Token" --expires 86400
    """
    args = ["--name", name]
    if profile:
        args.extend(["--profile", profile])
    if audience:
        args.extend(["--audience", audience])
    if expires:
        args.extend(["--expires", str(expires)])

    result = run_skill_script_subprocess(SKILL_NAME, "create_token.py", args)
    ctx.exit(result.returncode)


@security.command(name="delete-token")
@click.argument("token_id")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def delete_token(ctx, token_id, profile):
    """Delete an authentication token.

    Example:
        splunk-skill security delete-token token_12345
    """
    args = [token_id]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "delete_token.py", args)
    ctx.exit(result.returncode)


@security.command(name="list-users")
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
        splunk-skill security list-users
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_users.py", args)
    ctx.exit(result.returncode)


@security.command(name="list-roles")
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
        splunk-skill security list-roles
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_roles.py", args)
    ctx.exit(result.returncode)


@security.command()
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def capabilities(ctx, profile, output):
    """Get current user capabilities.

    Example:
        splunk-skill security capabilities
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_capabilities.py", args)
    ctx.exit(result.returncode)


@security.command()
@click.argument("path")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def acl(ctx, path, profile, output):
    """Get ACL for a resource.

    Example:
        splunk-skill security acl /servicesNS/admin/search/saved/searches/MySavedSearch
    """
    args = [path]
    if profile:
        args.extend(["--profile", profile])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_acl.py", args)
    ctx.exit(result.returncode)


@security.command()
@click.argument("capability")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.pass_context
def check(ctx, capability, profile):
    """Check if current user has a capability.

    Example:
        splunk-skill security check admin_all_objects
    """
    args = [capability]
    if profile:
        args.extend(["--profile", profile])

    result = run_skill_script_subprocess(SKILL_NAME, "check_permission.py", args)
    ctx.exit(result.returncode)
