"""
Contact models for the Konigle SDK.

Contact information of individuals for email marketing, including
purchase history, consent preferences, and customer data.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from konigle.models.base import CreateModel, TimestampedResource, UpdateModel

# Type alias for contact source
ContactSource = Literal["purchase", "lead", "migration", "unknown"]


class ContactUpdateLTV(BaseModel):
    """
    Model for updating contact LTV.

    Adds revenue to a contact's lifetime value, typically from
    a purchase or transaction.
    """

    email: EmailStr = Field(
        title="Contact Email",
        description="Email address of the contact to update.",
    )
    """Email address of the contact to update."""

    value: Decimal = Field(
        title="LTV Value",
        description="Value to add to the contact's LTV (positive).",
        gt=0,
        max_digits=19,
        decimal_places=2,
    )
    """Value to add to the contact's LTV (must be positive)."""

    currency: str = Field(
        title="Currency",
        description="Currency code (ISO 4217) for the LTV value.",
        max_length=3,
    )
    """Currency code (ISO 4217) for the LTV value."""


class MarketingConsent(BaseModel):
    """
    Marketing consent preferences for different channels.

    Tracks whether a contact has consented to receive marketing
    communications through email, SMS, and WhatsApp.
    """

    email: bool = Field(
        default=True,
        title="Email Consent",
        description="Whether contact has consented to email marketing.",
    )
    """Email marketing consent."""

    sms: bool = Field(
        default=True,
        title="SMS Consent",
        description="Whether contact has consented to SMS marketing.",
    )
    """SMS marketing consent."""

    whatsapp: bool = Field(
        default=True,
        title="WhatsApp Consent",
        description=("Whether contact has consented to WhatsApp marketing."),
    )
    """WhatsApp marketing consent."""

    model_config = ConfigDict(extra="ignore")


class BaseContact(BaseModel):
    """Base contact model with shared fields."""

    email: EmailStr = Field(
        title="Email Address",
        description="Email address of the contact.",
    )
    """Email address of the contact."""

    first_name: Optional[str] = Field(
        default="",
        title="First Name",
        description="First name of the contact.",
        max_length=100,
    )
    """First name of the contact."""

    last_name: Optional[str] = Field(
        default="",
        title="Last Name",
        description="Last name of the contact.",
        max_length=100,
    )
    """Last name of the contact."""

    phone: Optional[str] = Field(
        default="",
        title="Phone Number",
        description="Phone number of the contact.",
        max_length=20,
    )
    """Phone number of the contact."""

    whatsapp: Optional[str] = Field(
        default="",
        title="WhatsApp Number",
        description="WhatsApp number of the contact.",
        max_length=20,
    )
    """WhatsApp number of the contact."""

    country: Optional[str] = Field(
        default="",
        title="Country",
        description="Country name of the contact.",
        max_length=100,
    )
    """Country name of the contact."""

    source: ContactSource = Field(
        default="unknown",
        title="Contact Source",
        description=(
            "Source of the contact (purchase, lead, migration, unknown)."
        ),
    )
    """Source of the contact (purchase, lead, migration, or unknown)."""

    tags: list[str] = Field(
        default_factory=list,
        title="Tags",
        description=("Tags associated with the contact for organization."),
    )
    """Tags associated with the contact."""

    marketing_consent: MarketingConsent = Field(
        default_factory=MarketingConsent,
        title="Marketing Consent",
        description=("Marketing consent preferences (email, sms, whatsapp)."),
    )
    """Marketing consent preferences (email, sms, whatsapp)."""


class Contact(BaseContact, TimestampedResource):
    """
    Contact information for email marketing.

    Represents an individual contact with their personal information,
    consent preferences, purchase history, and customer data for
    email marketing campaigns.
    """

    customer_id: Optional[str] = Field(
        default="",
        title="Customer ID",
        description="Customer ID from the e-commerce system.",
        max_length=40,
    )
    """Customer ID from the e-commerce system."""

    ltv: Optional[Decimal] = Field(
        default=None,
        title="Lifetime Value",
        description="Lifetime value of the contact.",
        max_digits=19,
        decimal_places=2,
    )
    """Lifetime value of the contact."""

    ltv_currency: str = Field(
        default="USD",
        title="LTV Currency",
        description="Currency code for lifetime value (ISO 4217).",
        max_length=3,
    )
    """Currency code for lifetime value (ISO 4217)."""

    last_purchased_at: Optional[datetime] = Field(
        default=None,
        title="Last Purchase Date",
        description="When the contact last made a purchase.",
    )
    """When the contact last made a purchase."""

    def __str__(self) -> str:
        return (
            f"Contact(id={self.id} email={self.email} "
            f"source={self.source})"
        )


class ContactCreate(BaseContact, CreateModel):
    """Model for creating a new contact."""


class ContactUpdate(UpdateModel):
    """
    Model for updating an existing contact.

    Note: ltv, ltv_currency, and last_purchased_at are managed
    automatically by the system based on purchases and cannot
    be updated directly.
    """

    email: Optional[EmailStr] = Field(
        default=None,
        title="Email Address",
        description="Email address of the contact.",
    )
    """Email address of the contact."""

    first_name: Optional[str] = Field(
        default=None,
        title="First Name",
        description="First name of the contact.",
        max_length=100,
    )
    """First name of the contact."""

    last_name: Optional[str] = Field(
        default=None,
        title="Last Name",
        description="Last name of the contact.",
        max_length=100,
    )
    """Last name of the contact."""

    phone: Optional[str] = Field(
        default=None,
        title="Phone Number",
        description="Phone number of the contact.",
        max_length=20,
    )
    """Phone number of the contact."""

    whatsapp: Optional[str] = Field(
        default=None,
        title="WhatsApp Number",
        description="WhatsApp number of the contact.",
        max_length=20,
    )
    """WhatsApp number of the contact."""

    country: Optional[str] = Field(
        default=None,
        title="Country",
        description="Country name of the contact.",
        max_length=100,
    )
    """Country name of the contact."""

    source: Optional[ContactSource] = Field(
        default=None,
        title="Contact Source",
        description=(
            "Source of the contact (purchase, lead, migration, unknown)."
        ),
    )
    """Source of the contact (purchase, lead, migration, or unknown)."""

    tags: Optional[list[str]] = Field(
        default=None,
        title="Tags",
        description=("Tags associated with the contact for organization."),
    )
    """Tags associated with the contact."""

    marketing_consent: Optional[MarketingConsent] = Field(
        default=None,
        title="Marketing Consent",
        description=("Marketing consent preferences (email, sms, whatsapp)."),
    )
    """Marketing consent preferences (email, sms, whatsapp)."""
