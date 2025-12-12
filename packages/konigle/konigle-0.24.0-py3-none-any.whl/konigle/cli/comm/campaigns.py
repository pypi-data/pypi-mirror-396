"""
CLI commands for campaign management operations.
"""

from typing import Optional

import click

from konigle import models
from konigle.cli.comm.base import comm
from konigle.cli.main import get_client
from konigle.filters.comm import CampaignFilters


@comm.group()
def campaigns() -> None:
    """Campaign management commands."""
    pass


@campaigns.command("create")
@click.option("--name", "-n", required=True, help="Name of the campaign")
@click.option(
    "--audience",
    "-a",
    required=True,
    help="Audience ID for targeting",
)
@click.option(
    "--email-channel",
    required=True,
    help="Email channel ID to use",
)
@click.option(
    "--email-template",
    required=True,
    help="Email template ID to use",
)
@click.option("--description", "-d", help="Description of the campaign")
@click.option(
    "--scheduled-at",
    help="When to send (ISO format, e.g. 2024-01-15T10:00:00)",
)
@click.option(
    "--execution-duration",
    type=int,
    help="Duration in minutes to spread sends (max 1440)",
)
@click.option("--from-email", help="Override from email address")
@click.option("--from-name", help="Override from name")
@click.option("--reply-to-email", help="Override reply-to email address")
@click.option("--reply-to-name", help="Override reply-to name")
@click.option("--utm-code", help="UTM campaign code for tracking")
@click.pass_context
def create_campaign(
    ctx: click.Context,
    name: str,
    audience: str,
    email_channel: str,
    email_template: str,
    description: Optional[str],
    scheduled_at: Optional[str],
    execution_duration: Optional[int],
    from_email: Optional[str],
    from_name: Optional[str],
    reply_to_email: Optional[str],
    reply_to_name: Optional[str],
    utm_code: Optional[str],
) -> None:
    """Create a new campaign."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        # Parse scheduled_at if provided
        scheduled_dt = None
        if scheduled_at:
            from datetime import datetime

            try:
                scheduled_dt = datetime.fromisoformat(scheduled_at)
            except ValueError:
                click.echo(
                    "✗ Error: Invalid date format. Use ISO format "
                    "(e.g. 2024-01-15T10:00:00)",
                    err=True,
                )
                ctx.exit(1)

        campaign_data = models.CampaignCreate(
            name=name,
            channel_type="email",
            email_channel=email_channel,
            email_template=email_template,
            audience=audience,
            description=description or "",
            scheduled_at=scheduled_dt,
            execution_duration_minutes=execution_duration,
            from_email=from_email or "",
            from_name=from_name or "",
            reply_to_email=reply_to_email or "",
            reply_to_name=reply_to_name or "",
            utm_code=utm_code or "",
        )

        result = client.campaigns.create(campaign_data)

        click.echo("✓ Campaign created successfully!")
        click.echo(f"  ID: {result.id}")
        click.echo(f"  Name: {result.name}")
        click.echo(f"  Status: {result.status}")
        click.echo(f"  Channel: {result.channel_type}")
        if result.scheduled_at:
            click.echo(f"  Scheduled: {result.scheduled_at}")
        if result.utm_code:
            click.echo(f"  UTM Code: {result.utm_code}")

    except Exception as e:
        click.echo(f"✗ Error creating campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("list")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.option("--search", "-q", help="Search in name and description")
@click.option(
    "--status",
    type=click.Choice(
        [
            "draft",
            "scheduled",
            "running",
            "completed",
            "paused",
            "cancelled",
            "failed",
        ]
    ),
    help="Filter by status",
)
@click.option("--audience", help="Filter by audience code")
@click.pass_context
def list_campaigns(
    ctx: click.Context,
    page: int,
    page_size: int,
    search: Optional[str],
    status: Optional[str],
    audience: Optional[str],
) -> None:
    """List campaigns."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        filters = CampaignFilters(
            q=search,
            status=status,  # type: ignore
            audience=audience,
        )

        result = client.campaigns.list(
            page=page, page_size=page_size, filters=filters
        )

        if not result.payload:
            click.echo("No campaigns found.")
            return

        click.echo(f"Campaigns (page {page}):")
        click.echo()

        for campaign in result.payload:
            click.echo(campaign)

    except Exception as e:
        click.echo(f"✗ Error listing campaigns: {e}", err=True)
        ctx.exit(1)


@campaigns.command("get")
@click.argument("campaign_id")
@click.pass_context
def get_campaign(ctx: click.Context, campaign_id: str) -> None:
    """Get a campaign by ID with execution details."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        campaign = client.campaigns.get(campaign_id)

        click.echo("✓ Campaign details:")
        click.echo(f"{campaign.model_dump_json(indent=2)}")

    except Exception as e:
        click.echo(f"✗ Error getting campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("update")
@click.argument("campaign_id")
@click.option("--name", "-n", help="New name")
@click.option("--description", "-d", help="New description")
@click.option("--audience", help="New audience ID")
@click.option("--email-channel", help="New email channel ID")
@click.option("--email-template", help="New email template ID")
@click.option(
    "--scheduled-at",
    help="New scheduled time (ISO format)",
)
@click.option(
    "--execution-duration",
    type=int,
    help="New execution duration in minutes",
)
@click.option("--from-email", help="New from email")
@click.option("--from-name", help="New from name")
@click.option("--reply-to-email", help="New reply-to email")
@click.option("--reply-to-name", help="New reply-to name")
@click.option("--utm-code", help="New UTM code")
@click.pass_context
def update_campaign(
    ctx: click.Context,
    campaign_id: str,
    name: Optional[str],
    description: Optional[str],
    audience: Optional[str],
    email_channel: Optional[str],
    email_template: Optional[str],
    scheduled_at: Optional[str],
    execution_duration: Optional[int],
    from_email: Optional[str],
    from_name: Optional[str],
    reply_to_email: Optional[str],
    reply_to_name: Optional[str],
    utm_code: Optional[str],
) -> None:
    """Update a campaign."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if audience is not None:
            update_data["audience"] = audience
        if email_channel is not None:
            update_data["email_channel"] = email_channel
        if email_template is not None:
            update_data["email_template"] = email_template
        if scheduled_at is not None:
            from datetime import datetime

            try:
                update_data["scheduled_at"] = datetime.fromisoformat(
                    scheduled_at
                )
            except ValueError:
                click.echo(
                    "✗ Error: Invalid date format. Use ISO format",
                    err=True,
                )
                ctx.exit(1)
        if execution_duration is not None:
            update_data["execution_duration_minutes"] = execution_duration
        if from_email is not None:
            update_data["from_email"] = from_email
        if from_name is not None:
            update_data["from_name"] = from_name
        if reply_to_email is not None:
            update_data["reply_to_email"] = reply_to_email
        if reply_to_name is not None:
            update_data["reply_to_name"] = reply_to_name
        if utm_code is not None:
            update_data["utm_code"] = utm_code

        if not update_data:
            click.echo("No update fields provided.", err=True)
            ctx.exit(1)

        campaign_update = models.CampaignUpdate(**update_data)
        result = client.campaigns.update(campaign_id, campaign_update)

        click.echo("✓ Campaign updated successfully!")
        click.echo("Details:")
        click.echo(result.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error updating campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("delete")
@click.argument("campaign_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_campaign(
    ctx: click.Context,
    campaign_id: str,
    yes: bool,
) -> None:
    """Delete a campaign."""
    if not yes:
        if not click.confirm(
            f"Are you sure you want to delete campaign {campaign_id}?"
        ):
            click.echo("Cancelled.")
            return

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        client.campaigns.delete(campaign_id)

        click.echo(f"✓ Campaign {campaign_id} deleted successfully!")

    except Exception as e:
        click.echo(f"✗ Error deleting campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("start")
@click.argument("campaign_id")
@click.pass_context
def start_campaign(ctx: click.Context, campaign_id: str) -> None:
    """Start a campaign (only works when status is draft or scheduled)."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        campaign = client.campaigns.start(campaign_id)

        click.echo("✓ Campaign started successfully!")
        click.echo("Details:")
        click.echo(campaign.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error starting campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("pause")
@click.argument("campaign_id")
@click.pass_context
def pause_campaign(ctx: click.Context, campaign_id: str) -> None:
    """Pause a running campaign."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        campaign = client.campaigns.pause(campaign_id)

        click.echo("✓ Campaign paused successfully!")
        click.echo("Details:")
        click.echo(campaign.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error pausing campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("resume")
@click.argument("campaign_id")
@click.pass_context
def resume_campaign(ctx: click.Context, campaign_id: str) -> None:
    """Resume a paused campaign."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        campaign = client.campaigns.resume(campaign_id)

        click.echo("✓ Campaign resumed successfully!")
        click.echo("Details:")
        click.echo(campaign.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error resuming campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("cancel")
@click.argument("campaign_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def cancel_campaign(ctx: click.Context, campaign_id: str, yes: bool) -> None:
    """Cancel a campaign (works when running, draft, or scheduled)."""
    if not yes:
        if not click.confirm(
            f"Are you sure you want to cancel campaign {campaign_id}?"
        ):
            click.echo("Cancelled.")
            return

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        campaign = client.campaigns.cancel(campaign_id)

        click.echo("✓ Campaign cancelled successfully!")
        click.echo("Details:")
        click.echo(campaign.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error cancelling campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("schedule")
@click.argument("campaign_id")
@click.option(
    "--scheduled-at",
    help="When to send (ISO format, e.g., 2024-01-15T10:00:00)",
)
@click.pass_context
def schedule_campaign(
    ctx: click.Context,
    campaign_id: str,
    scheduled_at: Optional[str],
) -> None:
    """Schedule or reschedule a campaign."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        campaign = client.campaigns.schedule(campaign_id, scheduled_at)

        click.echo("✓ Campaign scheduled successfully!")
        click.echo("Details:")
        click.echo(campaign.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error scheduling campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("add-ltv")
@click.argument("campaign_id")
@click.option(
    "--contact-email",
    help="Email of the contact who made the purchase (optional)",
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
def add_campaign_ltv(
    ctx: click.Context,
    campaign_id: str,
    contact_email: Optional[str],
    value: float,
    currency: str,
) -> None:
    """Add LTV (Lifetime Value) to a campaign from a purchase."""
    try:
        from decimal import Decimal

        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        ltv_data = models.CampaignAddLTV(
            contact_email=contact_email,
            value=Decimal(str(value)),
            currency=currency,
        )

        campaign = client.campaigns.add_ltv(campaign_id, ltv_data)

        click.echo("✓ LTV added to campaign successfully!")
        click.echo("Details:")
        click.echo(campaign.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error adding LTV to campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("new-email-campaign")
@click.option("--name", "-n", required=True, help="Campaign name")
@click.option(
    "--email-channel",
    required=True,
    help="Email channel code to use",
)
@click.option(
    "--tag",
    "tags",
    required=True,
    multiple=True,
    help="Contact tags for audience (can be used multiple times)",
)
@click.option("--subject", "-s", required=True, help="Email subject line")
@click.option("--body-html", required=True, help="HTML body content")
@click.option("--body-text", help="Plain text body content")
@click.option("--description", "-d", help="Campaign description")
@click.option("--utm-code", help="UTM campaign code for tracking")
@click.option("--from-email", help="Override from email")
@click.option("--from-name", help="Override from name")
@click.option("--reply-to-email", help="Override reply-to email")
@click.option("--reply-to-name", help="Override reply-to name")
@click.option(
    "--scheduled-at",
    help="When to send (ISO format, e.g., 2024-01-15T10:00:00)",
)
@click.option(
    "--execution-duration",
    type=int,
    help="Duration in minutes to spread sends (max 1440)",
)
@click.option(
    "--audience-name", help="Name for audience (defaults to campaign name)"
)
@click.option(
    "--template-name", help="Name for template (defaults to campaign name)"
)
@click.pass_context
def new_email_campaign(
    ctx: click.Context,
    name: str,
    email_channel: str,
    tags: tuple,
    subject: str,
    body_html: str,
    body_text: Optional[str],
    description: Optional[str],
    utm_code: Optional[str],
    from_email: Optional[str],
    from_name: Optional[str],
    reply_to_email: Optional[str],
    reply_to_name: Optional[str],
    scheduled_at: Optional[str],
    execution_duration: Optional[int],
    audience_name: Optional[str],
    template_name: Optional[str],
) -> None:
    """Create a new email campaign with audience and template in one step."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        # Parse scheduled_at if provided
        scheduled_dt = None
        if scheduled_at:
            from datetime import datetime

            try:
                scheduled_dt = datetime.fromisoformat(scheduled_at)
            except ValueError:
                click.echo(
                    "✗ Error: Invalid date format. Use ISO format",
                    err=True,
                )
                ctx.exit(1)

        campaign_data = models.CampaignCreateEmail(
            campaign_name=name,
            email_channel=email_channel,
            contact_tags=list(tags),
            subject=subject,
            body_html=body_html,
            body_text=body_text or "",
            description=description or "",
            utm_code=utm_code or "",
            from_email=from_email or "",
            from_name=from_name or "",
            reply_to_email=reply_to_email or "",
            reply_to_name=reply_to_name or "",
            scheduled_at=scheduled_dt,
            execution_duration_minutes=execution_duration,
            audience_name=audience_name or "",
            template_name=template_name or "",
        )

        campaign = client.campaigns.new_email_campaign(campaign_data)

        click.echo("✓ Email campaign created successfully!")
        click.echo("Details:")
        click.echo(campaign.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error creating email campaign: {e}", err=True)
        ctx.exit(1)


@campaigns.command("send-test-email")
@click.argument("campaign_id")
@click.option(
    "--email",
    "-e",
    "email_address",
    required=True,
    help="Email address to send test email to",
)
@click.pass_context
def send_test_email(
    ctx: click.Context,
    campaign_id: str,
    email_address: str,
) -> None:
    """Send a test email for the specified email campaign."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.campaigns.send_test_email(campaign_id, email_address)

        click.echo("✓ Test email sent successfully!")
        click.echo(f"  Sent to: {email_address}")
        click.echo(f"  Response: {result}")

    except Exception as e:
        click.echo(f"✗ Error sending test email: {e}", err=True)
        ctx.exit(1)
