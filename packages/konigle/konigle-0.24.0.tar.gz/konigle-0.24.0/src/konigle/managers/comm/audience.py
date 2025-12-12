"""
Audience managers for the Konigle SDK.

This module provides managers for audience resources, enabling
audience segment management operations including CRUD operations.
"""

from typing import cast

from konigle.filters.comm import AudienceFilters
from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.comm.audience import (
    Audience,
    AudienceCreate,
    AudienceUpdate,
)


class BaseAudienceManager:
    """Base class for audience managers with shared configuration."""

    resource_class = Audience
    """The resource model class this manager handles."""

    resource_update_class = AudienceUpdate
    """The model class used for updating resources."""

    filter_class = AudienceFilters
    """The filter model class for this resource type."""

    base_path = "/reachout/api/v1/audiences"
    """The API base path for this resource type."""


class AudienceManager(BaseAudienceManager, BaseSyncManager):
    """Synchronous manager for audience resources."""

    def create(self, data: AudienceCreate) -> Audience:
        """
        Create a new audience.

        Args:
            data: Audience creation data including all required fields

        Returns:
            Created audience instance with Active Record capabilities

        Example:
            ```python
            from konigle.models.comm import AudienceCreate

            audience_data = AudienceCreate(
                name="Newsletter Subscribers",
                code="newsletter-subscribers",
                description="All contacts who subscribed to newsletter",
                tags=["newsletter", "engaged"],
            )
            audience = client.audiences.create(audience_data)
            print(f"Created audience: {audience.name}")
            ```
        """
        return cast(Audience, super().create(data))


class AsyncAudienceManager(BaseAudienceManager, BaseAsyncManager):
    """Asynchronous manager for audience resources."""

    async def create(self, data: AudienceCreate) -> Audience:
        """
        Create a new audience.

        Args:
            data: Audience creation data including all required fields

        Returns:
            Created audience instance with Active Record capabilities

        Example:
            ```python
            from konigle.models.comm import AudienceCreate

            audience_data = AudienceCreate(
                name="Newsletter Subscribers",
                code="newsletter-subscribers",
                description="All contacts who subscribed to newsletter",
                tags=["newsletter", "engaged"],
            )
            audience = await client.audiences.create(audience_data)
            print(f"Created audience: {audience.name}")
            ```
        """
        return cast(Audience, await super().create(data))
