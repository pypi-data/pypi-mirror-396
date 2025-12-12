"""
Form models for the Konigle SDK.

This module provides models for form resources from the forms service.
Forms have integer IDs as they come from a separate service.
"""

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Set

from pydantic import Field

from konigle.models.base import BaseResource, CreateModel, TimestampMixin


class Form(BaseResource, TimestampMixin):
    """
    Form resource model.

    Represents a form with fields from the forms service.
    Uses integer ID as it comes from a separate service.
    """

    id: int = Field(
        ...,
        title="Form ID",
        description="Unique identifier for the form.",
    )
    """Unique identifier for the form."""

    name: str = Field(
        ...,
        title="Form Name",
        description="The name of the form.",
    )
    """The name of the form."""

    slug: str = Field(
        ...,
        title="Slug",
        description="URL-friendly slug for the form.",
    )
    """URL-friendly slug for the form."""

    is_active: bool = Field(
        ...,
        title="Is Active",
        description="Whether the form is active.",
    )
    """Whether the form is active."""

    captcha_enabled: Optional[bool] = Field(
        default=None,
        title="Captcha Enabled",
        description="Whether CAPTCHA is enabled for this form.",
    )
    """Whether CAPTCHA is enabled for this form."""

    captcha_site_key: Optional[str] = Field(
        default=None,
        title="Captcha Site Key",
        description="CAPTCHA site key for client-side validation.",
    )
    """CAPTCHA site key for client-side validation."""

    endpoint_url: str = Field(
        ...,
        title="Endpoint URL",
        description="The URL endpoint for form submissions.",
        serialization_alias="submission_url",
    )
    """The URL endpoint for form submissions."""

    def __str__(self) -> str:
        return f"Form(id={self.id}, name='{self.name}', slug='{self.slug}')"


class FormCreate(CreateModel):
    """
    Form creation model.

    Defines fields required when creating a new form.
    The slug is auto-generated from the name.
    """

    name: str = Field(
        ...,
        title="Form Name",
        description="The name of the form.",
    )
    """The name of the form."""


class FormSubmission(BaseResource):
    """
    Form submission resource model.

    Represents a submission to a form with all metadata and spam detection.
    """

    id: int = Field(
        ...,
        title="Submission ID",
        description="Unique identifier for the form submission.",
    )
    """Unique identifier for the form submission."""

    form_name: Optional[str] = Field(
        default=None,
        title="Form Name",
        description="Name of the form that was submitted.",
    )
    """Name of the form that was submitted."""

    form_slug: Optional[str] = Field(
        default=None,
        title="Form Slug",
        description="Slug of the form that was submitted.",
    )
    """Slug of the form that was submitted."""

    form_data: Optional[Dict[str, Any]] = Field(
        default=None,
        title="Form Data",
        description="The submitted form data as key-value pairs.",
    )
    """The submitted form data as key-value pairs."""

    ip_address: str = Field(
        ...,
        title="IP Address",
        description="IP address of the submitter.",
    )
    """IP address of the submitter."""

    user_agent: Optional[str] = Field(
        default=None,
        title="User Agent",
        description="Browser user agent string.",
    )
    """Browser user agent string."""

    country: Optional[str] = Field(
        default=None,
        title="Country",
        description="ISO country code (2 characters).",
    )
    """ISO country code (2 characters)."""

    submitted_at: datetime = Field(
        ...,
        title="Submitted At",
        description="Timestamp when the form was submitted.",
    )
    """Timestamp when the form was submitted."""

    emails_sent: Optional[List[str]] = Field(
        default=None,
        title="Emails Sent",
        description="List of email addresses that were sent notifications.",
    )
    """List of email addresses that were sent notifications."""

    is_spam: bool = Field(
        default=False,
        title="Is Spam",
        description="Whether this submission was detected as spam.",
    )
    """Whether this submission was detected as spam."""

    spam_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        title="Spam Confidence",
        description="Confidence score for spam detection (0.0 to 1.0).",
    )
    """Confidence score for spam detection (0.0 to 1.0)."""

    spam_reason: Optional[str] = Field(
        default=None,
        title="Spam Reason",
        description="Reason why submission was marked as spam.",
    )
    """Reason why submission was marked as spam."""

    _detail_only_fields: ClassVar[Set[str]] = {
        "form_name",
        "form_slug",
        "form_data",
        "user_agent",
        "country",
        "submitted_at",
        "emails_sent",
        "is_spam",
        "spam_confidence",
        "spam_reason",
    }

    def __str__(self) -> str:
        spam_tag = " [SPAM]" if self.is_spam else ""
        return (
            f"FormSubmission(id={self.id}"
            f"submitted_at={self.submitted_at}, "
            f"country={self.country or 'N/A'}{spam_tag})"
        )


__all__ = [
    "Form",
    "FormCreate",
    "FormSubmission",
]
