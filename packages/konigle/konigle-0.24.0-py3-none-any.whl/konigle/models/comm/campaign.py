"""
Campaign models for the Konigle SDK.

Campaign configuration for sending messages across multiple channels.
Currently supports email campaigns with plans for WhatsApp, SMS, etc.
"""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, ClassVar, Literal, Optional, Set

from pydantic import AfterValidator, BaseModel, Field

from konigle.models.base import CreateModel, TimestampedResource, UpdateModel
from konigle.validators import validate_optional_email


class CampaignAddLTV(BaseModel):
    """
    Model for adding LTV to a campaign.

    Records revenue generated from a specific contact purchase
    and updates both campaign and contact LTV.
    """

    value: Decimal = Field(
        title="LTV Value",
        description="Value to add to campaign and contact LTV (positive).",
        gt=0,
        max_digits=19,
        decimal_places=2,
    )
    """Value to add to campaign and contact LTV (must be positive)."""

    currency: str = Field(
        title="Currency",
        description="Currency code (ISO 4217) for the LTV value.",
        max_length=3,
    )
    """Currency code (ISO 4217) for the LTV value."""

    contact_email: Annotated[
        Optional[str], AfterValidator(validate_optional_email)
    ] = Field(
        default=None,
        title="Contact Email",
        description=(
            "Email address of the contact who made the purchase. "
            "Optional if tracking aggregate campaign revenue."
        ),
    )
    """Email address of the contact who made the purchase."""


class CampaignCreateEmail(BaseModel):
    """
    Model for creating an email campaign with audience and template.

    This is a hybrid API that creates a campaign along with its
    associated audience and email template in a single operation.
    """

    campaign_name: str = Field(
        title="Campaign Name",
        description="Name of the campaign.",
        max_length=255,
    )
    """Name of the campaign."""

    email_channel: str = Field(
        title="Email Channel Code",
        description="Code of email channel to use.",
        max_length=50,
    )
    """Code of email channel to use."""

    contact_tags: list[str] = Field(
        title="Contact Tags",
        description="List of tags to filter contacts for audience.",
    )
    """List of tags to filter contacts for audience."""

    subject: str = Field(
        title="Email Subject",
        description="Email subject line.",
        max_length=255,
    )
    """Email subject line."""

    body_html: str = Field(
        title="HTML Body",
        description="HTML body content.",
    )
    """HTML body content."""

    body_text: Optional[str] = Field(
        default="",
        title="Text Body",
        description="Plain text body content.",
    )
    """Plain text body content."""

    description: Optional[str] = Field(
        default="",
        title="Description",
        description="Campaign description.",
    )
    """Campaign description."""

    utm_code: Optional[str] = Field(
        default="",
        title="UTM Code",
        description="UTM campaign code for tracking.",
        max_length=100,
    )
    """UTM campaign code for tracking."""

    from_email: Annotated[
        Optional[str], AfterValidator(validate_optional_email)
    ] = Field(
        default="",
        title="From Email",
        description="Override from email.",
    )
    """Override from email."""

    from_name: Optional[str] = Field(
        default="",
        title="From Name",
        description="Override from name. Required if account does not "
        "have default.",
        max_length=255,
    )
    """Override from name. Required if account does not have default."""

    reply_to_email: Annotated[
        Optional[str], AfterValidator(validate_optional_email)
    ] = Field(
        default="",
        title="Reply-To Email",
        description="Override reply-to email. Required if account does not "
        "have default.",
    )
    """Override reply-to email. Required if account does not have default."""

    reply_to_name: Optional[str] = Field(
        default="",
        title="Reply-To Name",
        description="Override reply-to name. Required if account does "
        "not have default.",
        max_length=255,
    )
    """Override reply-to name. Required if account does not have default."""

    scheduled_at: Optional[datetime] = Field(
        default=None,
        title="Scheduled At",
        description="When to send the campaign.",
    )
    """When to send the campaign."""

    execution_duration_minutes: Optional[int] = Field(
        default=None,
        title="Execution Duration (Minutes)",
        description="Duration in minutes to spread campaign sends.",
        ge=1,
        le=1440,
    )
    """Duration in minutes to spread campaign sends."""

    audience_name: Optional[str] = Field(
        default="",
        title="Audience Name",
        description="Name for audience (defaults to campaign_name).",
        max_length=255,
    )
    """Name for audience (defaults to campaign_name)."""

    template_name: Optional[str] = Field(
        default="",
        title="Template Name",
        description="Name for email template (defaults to campaign_name).",
        max_length=255,
    )
    """Name for email template (defaults to campaign_name)."""


# Type aliases for campaign enums
CampaignChannelType = Literal["email"]

CampaignStatus = Literal[
    "draft",
    "scheduled",
    "running",
    "completed",
    "paused",
    "cancelled",
    "failed",
]

CampaignExecutionStatus = Literal[
    "pending",
    "processing",
    "paused",
    "halted",
    "completed",
    "failed",
    "cancelled",
    "partially_completed",
]


class CampaignExecution(BaseModel):
    """
    Track execution of a campaign with process and status.

    Provides real-time tracking of campaign delivery progress,
    including send rates, delivery metrics, and error tracking.
    """

    status: CampaignExecutionStatus = Field(
        default="pending",
        title="Execution Status",
        description="Current execution status.",
    )
    """Current execution status."""

    started_at: Optional[datetime] = Field(
        default=None,
        title="Started At",
        description="When execution started.",
    )
    """When execution started."""

    completed_at: Optional[datetime] = Field(
        default=None,
        title="Completed At",
        description="When execution completed.",
    )
    """When execution completed."""

    expected_completion_at: Optional[datetime] = Field(
        default=None,
        title="Expected Completion At",
        description=("Expected completion time based on execution duration."),
    )
    """Expected completion time based on execution duration."""

    paused_at: Optional[datetime] = Field(
        default=None,
        title="Paused At",
        description="When the execution was paused (if applicable).",
    )
    """When the execution was paused (if applicable)."""

    resumed_at: Optional[datetime] = Field(
        default=None,
        title="Resumed At",
        description="When the execution was last resumed after being paused.",
    )
    """When the execution was last resumed after being paused."""

    cancelled_at: Optional[datetime] = Field(
        default=None,
        title="Cancelled At",
        description="When the execution was cancelled (if applicable).",
    )
    """When the execution was cancelled (if applicable)."""

    last_run_at: Optional[datetime] = Field(
        default=None,
        title="Last Run At",
        description=("When the last run completed for calculating send rate."),
    )
    """When the last run completed for calculating send rate."""

    next_run_at: Optional[datetime] = Field(
        default=None,
        title="Next Run At",
        description=(
            "When to run the next execution (for HALTED executions)."
        ),
    )
    """When to run the next execution (for HALTED executions)."""

    total_contacts: int = Field(
        default=0,
        title="Total Contacts",
        description="Total number of contacts to send to.",
    )
    """Total number of contacts to send to."""

    total_sent: int = Field(
        default=0,
        title="Total Sent",
        description="Number of messages successfully sent.",
    )
    """Number of messages successfully sent."""

    total_failed: int = Field(
        default=0,
        title="Total Failed",
        description="Number of messages that failed to send.",
    )
    """Number of messages that failed to send."""

    total_delivered: int = Field(
        default=0,
        title="Total Delivered",
        description="Number of messages delivered (from events).",
    )
    """Number of messages delivered (from events)."""

    total_bounced: int = Field(
        default=0,
        title="Total Bounced",
        description="Number of messages bounced (from events).",
    )
    """Number of messages bounced (from events)."""

    total_complained: int = Field(
        default=0,
        title="Total Complained",
        description="Number of spam complaints (from events).",
    )
    """Number of spam complaints (from events)."""

    total_opened: Optional[int] = Field(
        default=None,
        title="Total Opened",
        description="Number of messages opened (from events).",
    )
    """Number of messages opened (from events). NULL if not tracked."""

    total_clicked: Optional[int] = Field(
        default=None,
        title="Total Clicked",
        description="Number of messages with clicks (from events).",
    )
    """Number of messages with clicks (from events). NULL if not tracked."""

    error_message: Optional[str] = Field(
        default="",
        title="Error Message",
        description="Error message if execution failed.",
    )
    """Error message if execution failed."""


class BaseCampaign(BaseModel):
    """Base campaign model with shared fields."""

    channel_type: CampaignChannelType = Field(
        default="email",
        title="Channel Type",
        description="Type of channel for this campaign (email, etc.).",
    )
    """Type of channel for this campaign (email, etc.)."""

    email_channel: Optional[str] = Field(
        default=None,
        title="Email Channel ID",
        description=(
            "Channel to use for sending emails. Required for email "
            "campaigns."
        ),
    )
    """Channel to use for sending emails. Required for email campaigns."""

    email_template: Optional[str] = Field(
        default=None,
        title="Email Template ID",
        description="Email template to use. Required for email campaigns.",
    )
    """Email template to use. Required for email campaigns."""

    audience: str = Field(
        title="Audience ID",
        description="Target audience segment for this campaign.",
    )
    """Target audience segment for this campaign."""

    name: str = Field(
        title="Campaign Name",
        description="Name of the campaign.",
        max_length=255,
    )
    """Name of the campaign."""

    description: Optional[str] = Field(
        default="",
        title="Description",
        description="Description of the campaign purpose.",
    )
    """Description of the campaign purpose."""

    scheduled_at: Optional[datetime] = Field(
        default=None,
        title="Scheduled At",
        description="When to send the campaign (null for immediate send).",
    )
    """When to send the campaign (null for immediate send after starting)."""

    execution_duration_minutes: Optional[int] = Field(
        default=None,
        title="Execution Duration (Minutes)",
        description=(
            "Duration in minutes over which to spread campaign sends "
            "(max 1440). Null = send as fast as possible while honoring "
            "channel rate limit."
        ),
        ge=1,
        le=1440,
    )
    """Duration in minutes over which to spread campaign sends."""

    from_email: Annotated[
        Optional[str], AfterValidator(validate_optional_email)
    ] = Field(
        default="",
        title="From Email",
        description="Override from email (uses channel default if empty).",
    )
    """Override from email (uses channel default if empty)."""

    from_name: Optional[str] = Field(
        default="",
        title="From Name",
        description="Override from name (uses channel default if empty).",
        max_length=255,
    )
    """Override from name (uses channel default if empty)."""

    reply_to_email: Annotated[
        Optional[str], AfterValidator(validate_optional_email)
    ] = Field(
        default="",
        title="Reply-To Email",
        description=(
            "Override reply-to email (uses channel default if empty)."
        ),
    )
    """Override reply-to email (uses channel default if empty)."""

    reply_to_name: Optional[str] = Field(
        default="",
        title="Reply-To Name",
        description=(
            "Override reply-to name (uses channel default if empty)."
        ),
        max_length=255,
    )
    """Override reply-to name (uses channel default if empty)."""

    utm_code: Optional[str] = Field(
        default="",
        title="UTM Code",
        description=(
            "UTM campaign code for tracking performance in analytics."
        ),
        max_length=100,
    )
    """UTM campaign code for tracking performance in analytics."""


class Campaign(BaseCampaign, TimestampedResource):
    """
    Campaign configuration for sending messages across multiple channels.

    Currently supports email campaigns. Designed to support additional
    channels (WhatsApp, SMS, etc.) in the future.
    """

    status: CampaignStatus = Field(
        default="draft",
        title="Status",
        description="Current status of the campaign.",
    )
    """Current status of the campaign."""

    ltv: Optional[Decimal] = Field(
        default=None,
        title="Lifetime Value",
        description="Lifetime value (revenue) generated by this campaign.",
        max_digits=12,
        decimal_places=2,
    )
    """Lifetime value (revenue) generated by this campaign."""

    ltv_currency: str = Field(
        default="USD",
        title="LTV Currency",
        description="Currency code for lifetime value (ISO 4217).",
        max_length=3,
    )
    """Currency code for lifetime value (ISO 4217)."""

    execution: Optional[CampaignExecution] = Field(
        default=None,
        title="Execution Details",
        description="Execution tracking details (available in detail view).",
    )
    """Execution tracking details (available in detail view)."""

    _foreign_key_fields: ClassVar[Set[str]] = {"execution"}

    _detail_only_fields: ClassVar[Set[str]] = {"execution"}

    def __str__(self) -> str:
        return f"Campaign(id={self.id} name={self.name} status={self.status})"


class CampaignCreate(BaseCampaign, CreateModel):
    """Model for creating a new campaign."""


class CampaignUpdate(UpdateModel):
    """
    Model for updating an existing campaign.

    Note: ltv and ltv_currency are managed automatically by the system
    based on campaign performance and cannot be updated directly.
    Status transitions are handled by separate action endpoints.

    Campaign can only be updated when in draft and scheduled states. This does
    not hold for name and description which can be updated at any time.
    """

    email_channel: Optional[str] = Field(
        default=None,
        title="Email Channel ID",
        description="Channel to use for sending emails.",
    )
    """Channel to use for sending emails."""

    email_template: Optional[str] = Field(
        default=None,
        title="Email Template ID",
        description="Email template to use.",
    )
    """Email template to use."""

    audience: Optional[str] = Field(
        default=None,
        title="Audience ID",
        description="Target audience segment for this campaign.",
    )
    """Target audience segment for this campaign."""

    name: Optional[str] = Field(
        default=None,
        title="Campaign Name",
        description="Name of the campaign.",
        max_length=255,
    )
    """Name of the campaign."""

    description: Optional[str] = Field(
        default=None,
        title="Description",
        description="Description of the campaign purpose.",
    )
    """Description of the campaign purpose."""

    scheduled_at: Optional[datetime] = Field(
        default=None,
        title="Scheduled At",
        description="When to send the campaign.",
    )
    """When to send the campaign."""

    execution_duration_minutes: Optional[int] = Field(
        default=None,
        title="Execution Duration (Minutes)",
        description=(
            "Duration in minutes over which to spread campaign sends "
            "(max 1440)."
        ),
        ge=1,
        le=1440,
    )
    """Duration in minutes over which to spread campaign sends."""

    from_email: Annotated[
        Optional[str], AfterValidator(validate_optional_email)
    ] = Field(
        default=None,
        title="From Email",
        description="Override from email.",
    )
    """Override from email."""

    from_name: Optional[str] = Field(
        default=None,
        title="From Name",
        description="Override from name.",
        max_length=255,
    )
    """Override from name."""

    reply_to_email: Annotated[
        Optional[str], AfterValidator(validate_optional_email)
    ] = Field(
        default=None,
        title="Reply-To Email",
        description="Override reply-to email.",
    )
    """Override reply-to email."""

    reply_to_name: Optional[str] = Field(
        default=None,
        title="Reply-To Name",
        description="Override reply-to name.",
        max_length=255,
    )
    """Override reply-to name."""

    utm_code: Optional[str] = Field(
        default=None,
        title="UTM Code",
        description="UTM campaign code for tracking.",
        max_length=100,
    )
    """UTM campaign code for tracking."""
