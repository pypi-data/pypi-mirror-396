"""
CLI commands for contact management operations.
"""

from typing import Optional, cast

import click

from konigle.cli.comm.base import comm
from konigle.cli.main import get_client
from konigle.filters.comm import ContactFilters
from konigle.models import comm as models


@comm.group()
def contacts() -> None:
    """Contact management commands."""
    pass


@contacts.command("create")
@click.option(
    "--email", "-e", required=True, help="Email address of the contact"
)
@click.option("--first-name", help="First name of the contact")
@click.option("--last-name", help="Last name of the contact")
@click.option("--phone", help="Phone number of the contact")
@click.option("--whatsapp", help="WhatsApp number of the contact")
@click.option("--country", help="Country of the contact")
@click.option(
    "--source",
    type=click.Choice(["purchase", "lead", "migration", "unknown"]),
    default="unknown",
    help="Source of the contact",
)
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Tags for the contact (can be used multiple times)",
)
@click.option(
    "--email-consent/--no-email-consent",
    default=True,
    help="Email marketing consent",
)
@click.option(
    "--sms-consent/--no-sms-consent",
    default=True,
    help="SMS marketing consent",
)
@click.option(
    "--whatsapp-consent/--no-whatsapp-consent",
    default=True,
    help="WhatsApp marketing consent",
)
@click.pass_context
def create_contact(
    ctx: click.Context,
    email: str,
    first_name: Optional[str],
    last_name: Optional[str],
    phone: Optional[str],
    whatsapp: Optional[str],
    country: Optional[str],
    source: str,
    tags: tuple,
    email_consent: bool,
    sms_consent: bool,
    whatsapp_consent: bool,
) -> None:
    """Create a new contact."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        marketing_consent = models.MarketingConsent(
            email=email_consent,
            sms=sms_consent,
            whatsapp=whatsapp_consent,
        )

        contact_data = models.ContactCreate(
            email=email,
            first_name=first_name or "",
            last_name=last_name or "",
            phone=phone or "",
            whatsapp=whatsapp or "",
            country=country or "",
            source=source,  # type: ignore
            tags=list(tags) if tags else [],
            marketing_consent=marketing_consent,
        )

        result = client.contacts.create(contact_data)

        click.echo("✓ Contact created successfully!")
        click.echo("Details:")
        click.echo(result.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error creating contact: {e}", err=True)
        ctx.exit(1)


@contacts.command("list")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.option("--search", "-q", help="Search in email")
@click.option(
    "--source",
    type=click.Choice(["purchase", "lead", "migration", "unknown"]),
    help="Filter by source",
)
@click.option("--tags", help="Filter by tags (comma-separated)")
@click.pass_context
def list_contacts(
    ctx: click.Context,
    page: int,
    page_size: int,
    search: Optional[str],
    source: Optional[str],
    tags: Optional[str],
) -> None:
    """List contacts."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        filters = ContactFilters(
            q=search,
            source=source,  # type: ignore
            tags=tags,
        )

        result = client.contacts.list(
            page=page, page_size=page_size, filters=filters
        )

        if not result.payload:
            click.echo("No contacts found.")
            return

        click.echo(f"Contacts (page {page}):")
        click.echo()

        for contact in result.payload:
            click.echo(contact)

    except Exception as e:
        click.echo(f"✗ Error listing contacts: {e}", err=True)
        ctx.exit(1)


@contacts.command("get")
@click.argument("contact_id")
@click.pass_context
def get_contact(ctx: click.Context, contact_id: str) -> None:
    """Get a contact by ID."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        contact = client.contacts.get(contact_id)

        click.echo("✓ Contact details:")
        click.echo(f"{contact.model_dump_json(indent=2)}")

    except Exception as e:
        click.echo(f"✗ Error getting contact: {e}", err=True)
        ctx.exit(1)


@contacts.command("update")
@click.argument("contact_id")
@click.option("--email", "-e", help="New email address")
@click.option("--first-name", help="New first name")
@click.option("--last-name", help="New last name")
@click.option("--phone", help="New phone number")
@click.option("--whatsapp", help="New WhatsApp number")
@click.option("--country", help="New country")
@click.option(
    "--source",
    type=click.Choice(["purchase", "lead", "migration", "unknown"]),
    help="New source",
)
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Replace tags (can be used multiple times)",
)
@click.option(
    "--email-consent/--no-email-consent",
    default=None,
    help="Update email marketing consent",
)
@click.option(
    "--sms-consent/--no-sms-consent",
    default=None,
    help="Update SMS marketing consent",
)
@click.option(
    "--whatsapp-consent/--no-whatsapp-consent",
    default=None,
    help="Update WhatsApp marketing consent",
)
@click.pass_context
def update_contact(
    ctx: click.Context,
    contact_id: str,
    email: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    phone: Optional[str],
    whatsapp: Optional[str],
    country: Optional[str],
    source: Optional[str],
    tags: tuple,
    email_consent: Optional[bool],
    sms_consent: Optional[bool],
    whatsapp_consent: Optional[bool],
) -> None:
    """Update a contact."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        update_data = {}
        if email is not None:
            update_data["email"] = email
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if phone is not None:
            update_data["phone"] = phone
        if whatsapp is not None:
            update_data["whatsapp"] = whatsapp
        if country is not None:
            update_data["country"] = country
        if source is not None:
            update_data["source"] = source
        if tags:
            update_data["tags"] = list(tags)

        # Handle marketing consent updates
        if (
            email_consent is not None
            or sms_consent is not None
            or whatsapp_consent is not None
        ):
            # Get current contact to preserve existing consent values
            current_contact = cast(
                models.Contact, client.contacts.get(contact_id)
            )
            current_consent = current_contact.marketing_consent

            update_data["marketing_consent"] = models.MarketingConsent(
                email=(
                    email_consent
                    if email_consent is not None
                    else current_consent.email
                ),
                sms=(
                    sms_consent
                    if sms_consent is not None
                    else current_consent.sms
                ),
                whatsapp=(
                    whatsapp_consent
                    if whatsapp_consent is not None
                    else current_consent.whatsapp
                ),
            )

        if not update_data:
            click.echo("No update fields provided.", err=True)
            ctx.exit(1)

        contact_update = models.ContactUpdate(**update_data)
        result = client.contacts.update(contact_id, contact_update)

        click.echo("✓ Contact updated successfully!")
        click.echo("Details:")
        click.echo(result.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error updating contact: {e}", err=True)
        ctx.exit(1)


@contacts.command("delete")
@click.argument("contact_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_contact(
    ctx: click.Context,
    contact_id: str,
    yes: bool,
) -> None:
    """Delete a contact."""
    if not yes:
        if not click.confirm(
            f"Are you sure you want to delete contact {contact_id}?"
        ):
            click.echo("Cancelled.")
            return

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        client.contacts.delete(contact_id)

        click.echo(f"✓ Contact {contact_id} deleted successfully!")

    except Exception as e:
        click.echo(f"✗ Error deleting contact: {e}", err=True)
        ctx.exit(1)


@contacts.command("update-ltv")
@click.option(
    "--email",
    "-e",
    required=True,
    help="Email address of the contact",
)
@click.option(
    "--value",
    required=True,
    type=float,
    help="LTV value to add (positive number)",
)
@click.option(
    "--currency",
    required=True,
    help="Currency code (ISO 4217, e.g., USD)",
)
@click.pass_context
def update_contact_ltv(
    ctx: click.Context,
    email: str,
    value: float,
    currency: str,
) -> None:
    """Update contact LTV (Lifetime Value) from a purchase."""
    try:
        from decimal import Decimal

        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        ltv_data = models.ContactUpdateLTV(
            email=email,
            value=Decimal(str(value)),
            currency=currency,
        )

        contact = client.contacts.update_ltv(ltv_data)

        click.echo("✓ Contact LTV updated successfully!")
        click.echo(f"  Email: {contact.email}")
        name = f"{contact.first_name} {contact.last_name}".strip()
        if name:
            click.echo(f"  Name: {name}")
        click.echo(f"  Total LTV: {contact.ltv} {contact.ltv_currency}")

    except Exception as e:
        click.echo(f"✗ Error updating contact LTV: {e}", err=True)
        ctx.exit(1)
