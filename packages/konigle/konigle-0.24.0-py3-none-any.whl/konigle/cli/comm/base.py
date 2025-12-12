"""
Base module for communication CLI commands.

Defines the shared comm group used by all comm submodules.
"""

import click

from konigle.cli.main import cli


@cli.group()
def comm() -> None:
    """Communication management commands."""
    pass
