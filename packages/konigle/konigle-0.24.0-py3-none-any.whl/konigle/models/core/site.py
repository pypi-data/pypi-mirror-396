"""
Site models for the Konigle SDK.

This module provides models for site/website resources including
site details, mutation data, and list representations.
"""

from typing import Optional

from pydantic import Field

from konigle.models.base import BaseResource, UpdateModel


class Site(BaseResource):
    """
    Site resource model.

    Represents a complete site/website with all available fields
    from the detail endpoint.
    """

    name: str = Field(
        ...,
        title="Site Name",
        description="The name of the website.",
    )
    """The name of the site/website."""

    domain: str = Field(
        ...,
        title="Domain",
        description="The primary domain of the site.",
    )
    """The primary domain of the site."""

    konigle_domain: Optional[str] = Field(
        ...,
        title="Konigle Domain",
        description="The konigle.net domain.",
    )
    """The konigle.net domain."""

    uid: str = Field(
        ...,
        title="UID",
        description="Unique identifier of the site.",
    )
    """Unique identifier of the site."""

    password_enabled: bool = Field(
        default=False,
        title="Password Enabled",
        description="Whether password protection is enabled for the site.",
    )
    """Whether password protection is enabled for the site."""

    address1: Optional[str] = Field(
        default=None,
        title="Address Line 1",
        description="First line of the site's address.",
    )
    """First line of the site's address."""

    address2: Optional[str] = Field(
        default=None,
        title="Address Line 2",
        description="Second line of the site's address.",
    )
    """Second line of the site's address."""

    city: Optional[str] = Field(
        default=None,
        title="City",
        description="City of the site's address.",
    )
    """City of the site's address."""

    country: Optional[str] = Field(
        default=None,
        title="Country",
        description="Country of the site's address.",
    )
    """Country of the site's address."""

    province: Optional[str] = Field(
        default=None,
        title="Province/State",
        description="Province or state of the site's address.",
    )
    """Province or state of the site's address."""

    phone: Optional[str] = Field(
        default=None,
        title="Phone Number",
        description="Contact phone number for the site.",
    )
    """Contact phone number for the site."""

    email: Optional[str] = Field(
        default=None,
        title="Email",
        description="Contact email address for the site.",
    )
    """Contact email address for the site."""

    currency: Optional[str] = Field(
        default=None,
        title="Currency",
        description="Default currency code for the site.",
    )
    """Default currency code for the site."""

    asset_bucket: Optional[str] = Field(
        default=None,
        title="Asset Bucket",
        description="Storage bucket for site assets.",
    )
    """Storage bucket for site assets."""

    asset_domain: Optional[str] = Field(
        default=None,
        title="Asset Domain",
        description="CDN domain for serving site assets.",
    )
    """CDN domain for serving site assets."""

    # Define detail-only fields that are not available in list responses
    _detail_only_fields = {
        "address1",
        "address2",
        "city",
        "country",
        "phone",
        "email",
        "currency",
        "asset_bucket",
        "asset_domain",
    }

    @property
    def id(self) -> str:
        """Alias for uid to provide uniform interface."""
        return self.uid


class SiteUpdate(UpdateModel):
    """
    Site update model.

    Defines fields that can be updated for a site.
    Only includes mutable fields from the mutation serializer.
    """

    name: Optional[str] = Field(
        default=None,
        title="Site Name",
        description="The name of the site/website.",
    )
    """The name of the site/website."""

    address1: Optional[str] = Field(
        default=None,
        title="Address Line 1",
        description="First line of the site's address.",
    )
    """First line of the site's address."""

    address2: Optional[str] = Field(
        default=None,
        title="Address Line 2",
        description="Second line of the site's address.",
    )
    """Second line of the site's address."""

    city: Optional[str] = Field(
        default=None,
        title="City",
        description="City of the site's address.",
    )
    """City of the site's address."""

    country: Optional[str] = Field(
        default=None,
        title="Country",
        description="Country of the site's address.",
    )
    """Country of the site's address."""

    province: Optional[str] = Field(
        default=None,
        title="Province/State",
        description="Province or state of the site's address.",
    )
    """Province or state of the site's address."""

    phone: Optional[str] = Field(
        default=None,
        title="Phone Number",
        description="Contact phone number for the site.",
    )
    """Contact phone number for the site."""


__all__ = [
    "Site",
    "SiteUpdate",
]
