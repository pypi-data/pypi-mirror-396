"""
CLI commands for audience management operations.
"""

from typing import Optional

import click

from konigle import models
from konigle.cli.comm.base import comm
from konigle.cli.main import get_client
from konigle.filters.comm import AudienceFilters


@comm.group()
def audiences() -> None:
    """Audience segment management commands."""
    pass


@audiences.command("create")
@click.option("--name", "-n", required=True, help="Name of the audience")
@click.option(
    "--code",
    "-c",
    help="Unique code for the audience (slug format)",
)
@click.option("--description", "-d", help="Description of the audience")
@click.option(
    "--tag",
    "tags",
    required=True,
    multiple=True,
    help="Tags to filter contacts (can be used multiple times)",
)
@click.pass_context
def create_audience(
    ctx: click.Context,
    name: str,
    code: Optional[str],
    description: Optional[str],
    tags: tuple,
) -> None:
    """Create a new audience segment."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        audience_data = models.AudienceCreate(
            name=name,
            code=code,
            description=description or "",
            tags=list(tags),
        )

        result = client.audiences.create(audience_data)

        click.echo("✓ Audience created successfully!")
        click.echo("Details:")
        click.echo(result.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error creating audience: {e}", err=True)
        ctx.exit(1)


@audiences.command("list")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.option("--search", "-q", help="Search in name")
@click.option("--tags", help="Filter by tags (comma-separated)")
@click.pass_context
def list_audiences(
    ctx: click.Context,
    page: int,
    page_size: int,
    search: Optional[str],
    tags: Optional[str],
) -> None:
    """List audience segments."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        filters = AudienceFilters(
            q=search,
            tags=tags,
        )

        result = client.audiences.list(
            page=page, page_size=page_size, filters=filters
        )

        if not result.payload:
            click.echo("No audiences found.")
            return

        click.echo(f"Audiences (page {page}):")
        click.echo()

        for audience in result.payload:
            click.echo(audience)

    except Exception as e:
        click.echo(f"✗ Error listing audiences: {e}", err=True)
        ctx.exit(1)


@audiences.command("get")
@click.argument("audience_id")
@click.pass_context
def get_audience(ctx: click.Context, audience_id: str) -> None:
    """Get an audience by ID."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        audience = client.audiences.get(audience_id)

        click.echo("✓ Audience details:")
        click.echo(f"{audience.model_dump_json(indent=2)}")

    except Exception as e:
        click.echo(f"✗ Error getting audience: {e}", err=True)
        ctx.exit(1)


@audiences.command("update")
@click.argument("audience_id")
@click.option("--name", "-n", help="New name")
@click.option("--code", "-c", help="New code")
@click.option("--description", "-d", help="New description")
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Replace tags (can be used multiple times)",
)
@click.pass_context
def update_audience(
    ctx: click.Context,
    audience_id: str,
    name: Optional[str],
    code: Optional[str],
    description: Optional[str],
    tags: tuple,
) -> None:
    """Update an audience."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if code is not None:
            update_data["code"] = code
        if description is not None:
            update_data["description"] = description
        if tags:
            update_data["tags"] = list(tags)

        if not update_data:
            click.echo("No update fields provided.", err=True)
            ctx.exit(1)

        audience_update = models.AudienceUpdate(**update_data)
        result = client.audiences.update(audience_id, audience_update)

        click.echo("✓ Audience updated successfully!")
        click.echo("Details:")
        click.echo(result.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error updating audience: {e}", err=True)
        ctx.exit(1)


@audiences.command("delete")
@click.argument("audience_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_audience(
    ctx: click.Context,
    audience_id: str,
    yes: bool,
) -> None:
    """Delete an audience."""
    if not yes:
        if not click.confirm(
            f"Are you sure you want to delete audience {audience_id}?"
        ):
            click.echo("Cancelled.")
            return

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        client.audiences.delete(audience_id)

        click.echo(f"✓ Audience {audience_id} deleted successfully!")

    except Exception as e:
        click.echo(f"✗ Error deleting audience: {e}", err=True)
        ctx.exit(1)
