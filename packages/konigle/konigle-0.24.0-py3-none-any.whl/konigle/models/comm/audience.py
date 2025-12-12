"""
Audience models for the Konigle SDK.

Contact segment definitions based on tags for campaign targeting.
Audiences allow grouping contacts by tags for targeted marketing campaigns.
"""

from typing import Optional

from pydantic import BaseModel, Field

from konigle.models.base import CreateModel, TimestampedResource, UpdateModel


class BaseAudience(BaseModel):
    """Base audience model with shared fields."""

    name: str = Field(
        title="Audience Name",
        description="Name of the audience segment.",
        max_length=255,
    )
    """Name of the audience segment."""

    description: Optional[str] = Field(
        default="",
        title="Description",
        description="Description of the audience segment.",
    )
    """Description of the audience segment."""

    tags: list[str] = Field(
        title="Tags",
        description="Tags to filter contacts for this audience.",
    )
    """Tags to filter contacts for this audience."""


class Audience(BaseAudience, TimestampedResource):
    """
    Contact segment definition based on tags for campaign targeting.

    Audiences enable marketers to create targeted segments of contacts
    based on tags for use in email campaigns and other marketing activities.
    """

    code: str = Field(
        title="Audience Code",
        description="Unique code for the audience (slug format).",
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    """Unique code for the audience."""

    def __str__(self) -> str:
        return f"Audience(id={self.id} code={self.code} name={self.name})"


class AudienceCreate(BaseAudience, CreateModel):
    """Model for creating a new audience."""

    code: Optional[str] = Field(
        default=None,
        title="Audience Code",
        description="Unique code for the audience (slug format).",
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    """Unique code for the audience. If not provided, it will be auto-generated
    based on the name."""


class AudienceUpdate(UpdateModel):
    """Model for updating an existing audience."""

    name: Optional[str] = Field(
        default=None,
        title="Audience Name",
        description="Name of the audience segment.",
        max_length=255,
    )
    """Name of the audience segment."""

    code: Optional[str] = Field(
        default=None,
        title="Audience Code",
        description="Unique code for the audience (slug format).",
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    """Unique code for the audience."""

    description: Optional[str] = Field(
        default=None,
        title="Description",
        description="Description of the audience segment.",
    )
    """Description of the audience segment."""

    tags: Optional[list[str]] = Field(
        default=None,
        title="Tags",
        description="Tags to filter contacts for this audience.",
    )
    """Tags to filter contacts for this audience."""
