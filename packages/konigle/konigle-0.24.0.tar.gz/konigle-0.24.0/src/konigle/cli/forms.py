"""CLI commands for form management."""

import click

from konigle import models
from konigle.cli.main import cli, get_client


@cli.group()
def forms():
    """Manage forms and form submissions."""
    pass


@forms.command("list")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.pass_context
def list_forms(ctx: click.Context, page: int, page_size: int):
    """List all forms."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        result = client.forms.list(page=page, page_size=page_size)

        if not result.payload:
            click.echo("No forms found.")
            return

        click.echo(f"Forms (page {page}):")
        click.echo()

        for form in result.payload:
            click.echo(form)

    except Exception as e:
        click.echo(f"✗ Error listing forms: {e}", err=True)
        ctx.exit(1)


@forms.command("create")
@click.option("--name", "-n", required=True, help="Form name")
@click.pass_context
def create_form(ctx: click.Context, name: str):
    """Create a new form."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        form_data = models.FormCreate(name=name)

        result = client.forms.create(form_data)

        click.echo("✓ Form created successfully!")
        click.echo("Form details:")
        click.echo(result.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error creating form: {e}", err=True)
        ctx.exit(1)


@forms.command("get")
@click.argument("slug")
@click.pass_context
def get_form(ctx: click.Context, slug: str):
    """Get details of a specific form by slug."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        result = client.forms.get(slug=slug)

        click.echo("✓ Form details:")
        click.echo(result.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error getting form: {e}", err=True)
        ctx.exit(1)


@forms.command("submissions")
@click.argument("slug")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.pass_context
def list_submissions(ctx: click.Context, slug: str, page: int, page_size: int):
    """List submissions for a specific form by slug."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        result = client.forms.list_submissions(
            slug=slug, page=page, page_size=page_size
        )

        if not result.payload:
            click.echo(f"No submissions found for form '{slug}'.")
            return

        click.echo(f"Submissions for '{slug}' (page {page}):")
        click.echo()

        for submission in result.payload:
            click.echo(submission)

    except Exception as e:
        click.echo(f"✗ Error listing submissions: {e}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    forms()
