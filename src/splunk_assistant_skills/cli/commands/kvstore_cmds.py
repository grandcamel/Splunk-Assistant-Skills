"""KV Store commands for Splunk Assistant Skills CLI."""

import click

from splunk_assistant_skills.utils import run_skill_script_subprocess

SKILL_NAME = "splunk-kvstore"


@click.group()
def kvstore():
    """App Key Value Store operations.

    Manage KV Store collections and records in Splunk apps.
    """
    pass


@kvstore.command(name="list")
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
def list_collections(ctx, profile, app, output):
    """List all KV Store collections.

    Example:
        splunk-skill kvstore list --app my_app
    """
    args = []
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "list_collections.py", args)
    ctx.exit(result.returncode)


@kvstore.command()
@click.argument("collection_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def create(ctx, collection_name, profile, app):
    """Create a new KV Store collection.

    Example:
        splunk-skill kvstore create my_collection --app my_app
    """
    args = [collection_name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "create_collection.py", args)
    ctx.exit(result.returncode)


@kvstore.command()
@click.argument("collection_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation.")
@click.pass_context
def delete(ctx, collection_name, profile, app, force):
    """Delete a KV Store collection.

    Example:
        splunk-skill kvstore delete my_collection --app my_app
    """
    args = [collection_name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if force:
        args.append("--force")

    result = run_skill_script_subprocess(SKILL_NAME, "delete_collection.py", args)
    ctx.exit(result.returncode)


@kvstore.command()
@click.argument("collection_name")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.option("--query", "-q", help="JSON query filter.")
@click.option("--limit", "-l", type=int, help="Maximum records to return.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.pass_context
def query(ctx, collection_name, profile, app, query, limit, output):
    """Query records from a KV Store collection.

    Example:
        splunk-skill kvstore query my_collection --query '{"status": "active"}'
    """
    args = [collection_name]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if query:
        args.extend(["--query", query])
    if limit:
        args.extend(["--limit", str(limit)])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "query_collection.py", args)
    ctx.exit(result.returncode)


@kvstore.command()
@click.argument("collection_name")
@click.argument("key")
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
def get(ctx, collection_name, key, profile, app, output):
    """Get a specific record from a KV Store collection.

    Example:
        splunk-skill kvstore get my_collection record_id_123
    """
    args = [collection_name, key]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])
    if output:
        args.extend(["--output", output])

    result = run_skill_script_subprocess(SKILL_NAME, "get_record.py", args)
    ctx.exit(result.returncode)


@kvstore.command()
@click.argument("collection_name")
@click.argument("data")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def insert(ctx, collection_name, data, profile, app):
    """Insert a record into a KV Store collection.

    Example:
        splunk-skill kvstore insert my_collection '{"name": "test", "value": 123}'
    """
    args = [collection_name, data]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "insert_record.py", args)
    ctx.exit(result.returncode)


@kvstore.command()
@click.argument("collection_name")
@click.argument("key")
@click.argument("data")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def update(ctx, collection_name, key, data, profile, app):
    """Update a record in a KV Store collection.

    Example:
        splunk-skill kvstore update my_collection record_id '{"value": 456}'
    """
    args = [collection_name, key, data]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "update_record.py", args)
    ctx.exit(result.returncode)


@kvstore.command(name="delete-record")
@click.argument("collection_name")
@click.argument("key")
@click.option("--profile", "-p", help="Splunk profile to use.")
@click.option("--app", "-a", default="search", help="App context.")
@click.pass_context
def delete_record(ctx, collection_name, key, profile, app):
    """Delete a record from a KV Store collection.

    Example:
        splunk-skill kvstore delete-record my_collection record_id_123
    """
    args = [collection_name, key]
    if profile:
        args.extend(["--profile", profile])
    if app:
        args.extend(["--app", app])

    result = run_skill_script_subprocess(SKILL_NAME, "delete_record.py", args)
    ctx.exit(result.returncode)
