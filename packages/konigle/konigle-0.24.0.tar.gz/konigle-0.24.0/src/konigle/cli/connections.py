"""CLI commands for connection management."""

import click

from konigle.cli.main import cli, get_client


@cli.group()
def connections():
    """Manage third-party API connections."""
    pass


@connections.command("list")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.pass_context
def list_connections(ctx: click.Context, page: int, page_size: int):
    """List connections."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        result = client.connections.list(page=page, page_size=page_size)

        if not result.payload:
            click.echo("No connections found.")
            return

        click.echo(f"Connections (page {page}):")
        click.echo()

        for connection in result.payload:
            click.echo(connection)

    except Exception as e:
        click.echo(f"✗ Error listing connections: {e}", err=True)
        ctx.exit(1)


@connections.command("get-credentials")
@click.argument("provider")
@click.pass_context
def get_credentials(ctx: click.Context, provider: str):
    """Get connection credentials by provider code."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        credentials = client.connections.get_credentials(provider)

        click.echo(f"✓ Fetched credentials for {provider} successfully!")
        click.echo("Credentials:")

        import json

        click.echo(json.dumps(credentials, indent=2))

    except Exception as e:
        click.echo(f"✗ Error getting credentials: {e}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    connections()
