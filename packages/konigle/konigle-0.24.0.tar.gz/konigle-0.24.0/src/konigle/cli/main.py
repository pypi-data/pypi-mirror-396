"""
Main CLI entry point for Konigle SDK.
"""

import os
from typing import Optional

import click

from konigle import Client
from konigle.cli.config import ConfigManager


def load_env_file(env_path: str = ".env") -> None:
    """Load environment variables from .env file if it exists."""
    if not os.path.exists(env_path):
        return

    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and not os.getenv(key):
                        os.environ[key] = value

    except Exception:
        pass  # Silently ignore errors reading .env file


def get_client(
    api_key: Optional[str] = None, base_url: Optional[str] = None
) -> Client:
    """Get a Konigle client instance with configuration."""
    # First priority: explicit parameters
    if api_key and base_url:
        return Client(api_key=api_key, base_url=base_url)

    # Second priority: active project configuration
    config_manager = ConfigManager()
    active_config = config_manager.get_active_project()

    if active_config:
        final_api_key = api_key or active_config["api_key"]
        final_base_url = base_url or active_config["base_url"]
    else:
        # Third priority: environment variables
        final_api_key = api_key or os.getenv("KONIGLE_API_KEY")
        final_base_url = base_url or os.getenv(
            "KONIGLE_BASE_URL", "https://tim.konigle.com"
        )

    if not final_api_key:
        raise click.ClickException(
            "API key required. Add a project with 'konigle projects add', "
            "set KONIGLE_API_KEY environment variable, or use --api-key option."
        )

    return Client(api_key=final_api_key, base_url=final_base_url)


@click.group()
@click.option("--api-key", help="Konigle API key")
@click.option("--base-url", help="API base URL")
@click.pass_context
def cli(
    ctx: click.Context, api_key: Optional[str], base_url: Optional[str]
) -> None:
    """Konigle SDK CLI tool."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url


# Load .env file at startup (when module is imported)
load_env_file()

# Import commands to register them
from konigle.cli import authors  # noqa
from konigle.cli import blogs  # noqa
from konigle.cli import components  # noqa
from konigle.cli import connections  # noqa
from konigle.cli import design  # noqa
from konigle.cli import folders  # noqa
from konigle.cli import forms  # noqa
from konigle.cli import glossary  # noqa
from konigle.cli import images  # noqa
from konigle.cli import pages  # noqa
from konigle.cli import product_images  # noqa
from konigle.cli import product_variants  # noqa
from konigle.cli import products  # noqa
from konigle.cli import projects  # noqa
from konigle.cli import site  # noqa
from konigle.cli import templates  # noqa
from konigle.cli import uploads  # noqa
from konigle.cli.comm import audiences  # noqa
from konigle.cli.comm import campaigns  # noqa
from konigle.cli.comm import contacts  # noqa
from konigle.cli.comm import email  # noqa

if __name__ == "__main__":
    cli()
