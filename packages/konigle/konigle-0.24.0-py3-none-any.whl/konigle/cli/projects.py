"""
Project management commands for Konigle CLI.
"""

from typing import Optional

import click

from konigle.cli.config import ConfigManager
from konigle.cli.main import cli


@cli.group()
def projects() -> None:
    """Manage Konigle projects."""
    pass


@projects.command()
@click.argument("name")
@click.option("--api-key", required=True, help="API key for the project")
@click.option("--base-url", help="Base URL for the project")
@click.option("--activate", is_flag=True, help="Set as active project")
def add(
    name: str, api_key: str, base_url: Optional[str], activate: bool
) -> None:
    """Add a new project configuration."""
    config_manager = ConfigManager()

    try:
        config_manager.add_project(name, api_key, base_url)

        if activate:
            config_manager.set_active_project(name)

        click.echo(f"Project '{name}' added successfully")
        if activate or not config_manager.get_active_project_name():
            click.echo(f"Project '{name}' is now active")

    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@projects.command()
@click.argument("name")
def remove(name: str) -> None:
    """Remove a project configuration."""
    config_manager = ConfigManager()

    try:
        config_manager.remove_project(name)
        click.echo(f"Project '{name}' removed successfully")

    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@projects.command()
@click.argument("name")
def activate(name: str) -> None:
    """Set a project as active."""
    config_manager = ConfigManager()

    try:
        config_manager.set_active_project(name)
        click.echo(f"Project '{name}' is now active")

    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@projects.command("list")
def list_projects() -> None:
    """List all configured projects."""
    config_manager = ConfigManager()
    projects_list = config_manager.list_projects()
    active_project = config_manager.get_active_project_name()

    if not projects_list:
        click.echo("No projects configured")
        return

    click.echo("Configured projects:")
    for name, config in projects_list.items():
        active_marker = " (active)" if name == active_project else ""
        click.echo(f"  {name}{active_marker}")
        click.echo(f"    Base URL: {config['base_url']}")


@projects.command()
def current() -> None:
    """Show the current active project."""
    config_manager = ConfigManager()
    active_project = config_manager.get_active_project_name()

    if active_project:
        config = config_manager.get_active_project()
        if config:
            click.echo(f"Active project: {active_project}")
            click.echo(f"Base URL: {config['base_url']}")
        else:
            click.echo(
                "Something wrong with the config. Active project found but "
                "details missing.",
                err=True,
            )
    else:
        click.echo("No active project set")
