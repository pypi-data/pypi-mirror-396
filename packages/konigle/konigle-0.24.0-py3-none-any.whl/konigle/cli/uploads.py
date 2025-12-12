"""
CLI commands for upload operations.
"""

from typing import Optional

import click

from konigle import models
from konigle.cli.main import cli, get_client


@cli.group()
def uploads() -> None:
    """Upload management commands."""
    pass


@uploads.command()
@click.option("--file", "-f", required=True, help="Path to file or URL")
@click.option("--name", "-n", help="Upload name")
@click.option("--tags", "-t", help="Comma-separated tags")
@click.option("--description", "-d", help="Optional description of the upload")
@click.pass_context
def create(
    ctx: click.Context,
    file: str,
    name: Optional[str],
    tags: Optional[str],
    description: Optional[str],
) -> None:
    """Create a new upload."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        upload_data = models.UploadCreate(
            name=name or "",
            tags=tags or "",
            file=file,
            description=description,
        )

        result = client.uploads.create(upload_data)

        click.echo("✓ Upload created successfully!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error creating upload: {e}", err=True)
        ctx.exit(1)


@uploads.command("list")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.pass_context
def list_uploads(
    ctx: click.Context,
    page: int,
    page_size: int,
) -> None:
    """List uploads."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        result = client.uploads.list(
            page=page,
            page_size=page_size,
        )

        if not result.payload:
            click.echo("No uploads found.")
            return

        click.echo(f"Uploads (page {page}):")
        click.echo()

        for upload in result.payload:
            click.echo(upload)

    except Exception as e:
        click.echo(f"✗ Error listing uploads: {e}", err=True)
        ctx.exit(1)


@uploads.command()
@click.argument("upload_id")
@click.pass_context
def get(
    ctx: click.Context,
    upload_id: str,
) -> None:
    """Get details of a specific upload."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.uploads.get(upload_id)

        click.echo("Upload details:")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error getting upload: {e}", err=True)
        ctx.exit(1)


@uploads.command()
@click.argument("upload_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete(
    ctx: click.Context,
    upload_id: str,
    yes: bool,
) -> None:
    """Delete an upload."""
    if not yes:
        if not click.confirm(
            f"Are you sure you want to delete upload {upload_id}?"
        ):
            click.echo("Cancelled.")
            return

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        client.uploads.delete(upload_id)

        click.echo(f"✓ Upload {upload_id} deleted successfully!")

    except Exception as e:
        click.echo(f"✗ Error deleting upload: {e}", err=True)
        ctx.exit(1)


@uploads.command("create-cloud-upload")
@click.option("--mime-type", "-m", required=True, help="MIME type of the file")
@click.option(
    "--file-size", "-s", required=True, type=int, help="File size in bytes"
)
@click.option("--filename", "-f", required=True, help="Filename")
@click.option("--name", "-n", help="Display name for the upload")
@click.pass_context
def create_cloud_upload(
    ctx: click.Context,
    mime_type: str,
    file_size: int,
    filename: str,
    name: Optional[str],
) -> None:
    """Create a presigned upload URL for direct to cloud upload."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        result = client.uploads.create_cloud_upload(
            mime_type=mime_type,
            file_size=file_size,
            filename=filename,
            name=name,
        )

        click.echo("✓ Cloud upload URL created successfully!")
        click.echo("Upload info:")
        for key, value in result.items():
            click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"✗ Error creating cloud upload: {e}", err=True)
        ctx.exit(1)


@uploads.command("mark-started")
@click.argument("upload_id")
@click.pass_context
def mark_started(
    ctx: click.Context,
    upload_id: str,
) -> None:
    """Mark upload as started (for cloud uploads)."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.uploads.mark_started(upload_id)

        click.echo(f"✓ Upload {upload_id} marked as started!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error marking upload as started: {e}", err=True)
        ctx.exit(1)


@uploads.command("mark-completed")
@click.argument("upload_id")
@click.pass_context
def mark_completed(
    ctx: click.Context,
    upload_id: str,
) -> None:
    """Mark upload as completed (for cloud uploads)."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.uploads.mark_completed(upload_id)

        click.echo(f"✓ Upload {upload_id} marked as completed!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error marking upload as completed: {e}", err=True)
        ctx.exit(1)


@uploads.command("mark-failed")
@click.argument("upload_id")
@click.pass_context
def mark_failed(
    ctx: click.Context,
    upload_id: str,
) -> None:
    """Mark upload as failed (for cloud uploads)."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.uploads.mark_failed(upload_id)

        click.echo(f"✓ Upload {upload_id} marked as failed!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error marking upload as failed: {e}", err=True)
        ctx.exit(1)
