"""CLI commands for website and business information management."""

import json

import click

from konigle.cli.main import cli, get_client
from konigle.models.core.site import SiteUpdate


@cli.group()
def website():
    """Manage website and business information."""
    pass


@website.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save northstar to file",
)
@click.pass_context
def get_northstar(ctx: click.Context, output: str | None):
    """Get the business northstar."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        content = client.website.get_northstar()

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Northstar saved to {output}")
        else:
            click.echo(content)

    except Exception as e:
        click.echo(f"Error getting northstar: {e}", err=True)


@website.command()
@click.option(
    "--content",
    help="Northstar information as string",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, readable=True),
    help="Path to northstar file",
)
@click.pass_context
def set_northstar(
    ctx: click.Context,
    content: str | None,
    file: str | None,
):
    """Set the business northstar."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    # Validate input
    if not content and not file:
        click.echo(
            "Error: Either --content or --file must be provided", err=True
        )
        return

    if content and file:
        click.echo("Error: Cannot specify both --content and --file", err=True)
        return

    # Get content from file or direct input
    northstar_content = content
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                northstar_content = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {e}", err=True)
            return

    try:
        client.website.set_northstar(northstar_content or "")
        click.echo("✅ Northstar updated successfully")

    except Exception as e:
        click.echo(f"Error setting northstar: {e}", err=True)


@website.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save business info to file",
)
@click.pass_context
def get_business_info(ctx: click.Context, output: str | None):
    """Get the business information."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        content = client.website.get_business_info()

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Business info saved to {output}")
        else:
            click.echo(content)

    except Exception as e:
        click.echo(f"Error getting business info: {e}", err=True)


@website.command()
@click.option(
    "--content",
    help="Business information as string",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, readable=True),
    help="Path to business info file",
)
@click.pass_context
def set_business_info(
    ctx: click.Context,
    content: str | None,
    file: str | None,
):
    """Set the business information."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    # Validate input
    if not content and not file:
        click.echo(
            "Error: Either --content or --file must be provided", err=True
        )
        return

    if content and file:
        click.echo("Error: Cannot specify both --content and --file", err=True)
        return

    # Get content from file or direct input
    info_content = content
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                info_content = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {e}", err=True)
            return

    try:
        client.website.set_business_info(info_content or "")
        click.echo("✅ Business info updated successfully")

    except Exception as e:
        click.echo(f"Error setting business info: {e}", err=True)


@website.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save website info to file",
)
@click.pass_context
def get_website_info(ctx: click.Context, output: str | None):
    """Get the website information."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        content = client.website.get_website_info()

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Website info saved to {output}")
        else:
            click.echo(content)

    except Exception as e:
        click.echo(f"Error getting website info: {e}", err=True)


@website.command()
@click.option(
    "--content",
    help="Website information as string",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, readable=True),
    help="Path to website info file",
)
@click.pass_context
def set_website_info(
    ctx: click.Context,
    content: str | None,
    file: str | None,
):
    """Set the website information."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    # Validate input
    if not content and not file:
        click.echo(
            "Error: Either --content or --file must be provided", err=True
        )
        return

    if content and file:
        click.echo("Error: Cannot specify both --content and --file", err=True)
        return

    # Get content from file or direct input
    info_content = content
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                info_content = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {e}", err=True)
            return

    try:
        client.website.set_website_info(info_content or "")
        click.echo("✅ Website info updated successfully")

    except Exception as e:
        click.echo(f"Error setting website info: {e}", err=True)


@website.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save design system to file",
)
@click.pass_context
def get_design_system(ctx: click.Context, output: str | None):
    """Get the design system information."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        content = client.website.get_design_system()

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ Design system saved to {output}")
        else:
            click.echo(content)

    except Exception as e:
        click.echo(f"Error getting design system: {e}", err=True)


@website.command()
@click.option(
    "--content",
    help="Design system information as string",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, readable=True),
    help="Path to design system file",
)
@click.pass_context
def set_design_system(
    ctx: click.Context,
    content: str | None,
    file: str | None,
):
    """Set the design system information."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    # Validate input
    if not content and not file:
        click.echo(
            "Error: Either --content or --file must be provided", err=True
        )
        return

    if content and file:
        click.echo("Error: Cannot specify both --content and --file", err=True)
        return

    # Get content from file or direct input
    info_content = content
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                info_content = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {e}", err=True)
            return

    try:
        client.website.set_design_system(info_content or "")
        click.echo("✅ Design system updated successfully")

    except Exception as e:
        click.echo(f"Error setting design system: {e}", err=True)


@website.command()
@click.argument("pathname")
@click.option(
    "--type",
    "url_type",
    type=click.Choice(["page", "folder"]),
    default="page",
    help="Type of URL to add (page or folder)",
)
@click.pass_context
def add_url(ctx: click.Context, pathname: str, url_type: str):
    """Add a URL to the website."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        result = client.website.add_url(pathname, url_type)  # type: ignore
        click.echo(f"✅ URL added successfully: {pathname}")
        if result:
            click.echo(f"Details:\n {result}")

    except Exception as e:
        click.echo(f"Error adding URL: {e}", err=True)


@website.command()
@click.argument("pathname")
@click.option(
    "--version",
    help="Page version to retrieve",
)
@click.pass_context
def get_url(ctx: click.Context, pathname: str, version: str | None):
    """Get URL details from the website."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        result = client.website.get_url(pathname, version)
        click.echo(f"URL details for {pathname}:")
        click.echo(result)

    except Exception as e:
        click.echo(f"Error getting URL: {e}", err=True)


@website.command("get")
@click.pass_context
def get_site(ctx: click.Context):
    """Get a specific site by ID."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        site = client.website.get()

        click.echo("✅ Fetched site successfully!")
        click.echo("Details:")
        click.echo(site.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"Error getting site: {e}", err=True)


@website.command("update")
@click.option("--name", help="Update the site name")
@click.option("--address1", help="Update address line 1")
@click.option("--address2", help="Update address line 2")
@click.option("--city", help="Update city")
@click.option("--country", help="Update country")
@click.option("--province", help="Update province/state")
@click.option("--phone", help="Update phone number")
@click.pass_context
def update(
    ctx: click.Context,
    name: str | None,
    address1: str | None,
    address2: str | None,
    city: str | None,
    country: str | None,
    province: str | None,
    phone: str | None,
):
    """Update a site."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    # Build update data from provided options
    update_data = {}
    if name is not None:
        update_data["name"] = name

    if address1 is not None:
        update_data["address1"] = address1
    if address2 is not None:
        update_data["address2"] = address2
    if city is not None:
        update_data["city"] = city
    if country is not None:
        update_data["country"] = country
    if province is not None:
        update_data["province"] = province
    if phone is not None:
        update_data["phone"] = phone

    if not update_data:
        click.echo("Error: No update fields provided", err=True)
        return

    try:

        site_update = SiteUpdate(**update_data)
        updated_site = client.website.update(site_update)

        click.echo("✅ Site updated successfully")
        click.echo("Details:")
        click.echo(updated_site.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"Error updating site: {e}", err=True)


@website.command("get-settings")
@click.pass_context
def get_settings(ctx: click.Context):
    """Get website settings."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        content = client.website.get_settings()
        click.echo("✅ Fetched website settings successfully!")
        click.echo("Details:")
        click.echo(json.dumps(content, indent=2))

    except Exception as e:
        click.echo(f"Error getting northstar: {e}", err=True)


@website.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save robots.txt to file",
)
@click.pass_context
def get_robots_txt(ctx: click.Context, output: str | None):
    """Get the robots.txt content."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    try:
        content = client.website.get_robots_txt()

        if not content:
            click.echo("robots.txt is not set. Default rules apply.")
            return

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            click.echo(f"✅ robots.txt saved to {output}")
        else:
            click.echo(content)

    except Exception as e:
        click.echo(f"Error getting robots.txt: {e}", err=True)


@website.command()
@click.option(
    "--content",
    help="robots.txt content as string",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, readable=True),
    help="Path to robots.txt file",
)
@click.pass_context
def set_robots_txt(
    ctx: click.Context,
    content: str | None,
    file: str | None,
):
    """Set the robots.txt content."""
    client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

    # Validate input
    if not content and not file:
        click.echo(
            "Error: Either --content or --file must be provided", err=True
        )
        return

    if content and file:
        click.echo("Error: Cannot specify both --content and --file", err=True)
        return

    # Get content from file or direct input
    robots_content = content
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                robots_content = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {e}", err=True)
            return

    try:
        client.website.set_robots_txt(robots_content or "")
        click.echo("✅ robots.txt updated successfully")

    except Exception as e:
        click.echo(f"Error setting robots.txt: {e}", err=True)


if __name__ == "__main__":
    website()
