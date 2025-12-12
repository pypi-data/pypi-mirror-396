"""
Email channel managers for the Konigle SDK.

This module provides managers for email channel resources, enabling
email channel management operations including CRUD operations.
"""

from typing import cast

from konigle.filters.comm import EmailChannelFilters
from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.comm.email.channel import (
    EmailChannel,
    EmailChannelCreate,
    EmailChannelUpdate,
)


class BaseEmailChannelManager:
    """Base class for email channel managers with shared configuration."""

    resource_class = EmailChannel
    """The resource model class this manager handles."""

    resource_update_class = EmailChannelUpdate
    """The model class used for updating resources."""

    filter_class = EmailChannelFilters
    """The filter model class for this resource type."""

    base_path = "/reachout/api/v1/channels"
    """The API base path for this resource type."""


class EmailChannelManager(BaseEmailChannelManager, BaseSyncManager):
    """Synchronous manager for email channel resources."""

    def create(self, data: EmailChannelCreate) -> EmailChannel:
        """
        Create a new email channel.

        Args:
            data: Email channel creation data including all required fields

        Returns:
            Created email channel instance with Active Record capabilities

        Example:
            ```python
            channel_data = EmailChannelCreate(
                code="transactional",
                channel_type=EmailChannelType.TRANSACTIONAL,
            )
            channel = client.email_channels.create(channel_data)
            print(f"Created channel: {channel.code}")
            ```
        """
        return cast(EmailChannel, super().create(data))

    def set_engagement_tracking(
        self, channel_id: str, enable: bool
    ) -> EmailChannel:
        """
        Enable or disable engagement tracking for the channel.

        Args:
            channel_id: ID of the channel to update
            enable: True to enable engagement tracking, False to disable

        Returns:
            Updated channel instance with engagement tracking setting

        Example:
            ```python
            channel = client.email_channels.set_engagement_tracking(
                "ch_123", True
            )
            print(f"Engagement tracking: {channel.enable_engagement_tracking}")
            ```
        """
        url = f"{self.base_path}/{channel_id}/set-engagement-tracking"
        response = self._session.post(url, json={"enable": enable})
        return cast(
            EmailChannel,
            self.create_resource(response.json(), is_partial=False),
        )


class AsyncEmailChannelManager(BaseEmailChannelManager, BaseAsyncManager):
    """Asynchronous manager for email channel resources."""

    async def create(self, data: EmailChannelCreate) -> EmailChannel:
        """
        Create a new email channel.

        Args:
            data: Email channel creation data including all required fields

        Returns:
            Created email channel instance with Active Record capabilities

        Example:
            ```python
            channel_data = EmailChannelCreate(
                code="transactional",
                channel_type=EmailChannelType.TRANSACTIONAL,
            )
            channel = await client.email_channels.create(channel_data)
            print(f"Created channel: {channel.code}")
            ```
        """
        return cast(EmailChannel, await super().create(data))

    async def set_engagement_tracking(
        self, channel_id: str, enable: bool
    ) -> EmailChannel:
        """
        Enable or disable engagement tracking for the channel.

        Args:
            channel_id: ID of the channel to update
            enable: True to enable engagement tracking, False to disable

        Returns:
            Updated channel instance with engagement tracking setting

        Example:
            ```python
            channel = await client.email_channels.set_engagement_tracking(
                "ch_123", True
            )
            print(f"Engagement tracking: {channel.enable_engagement_tracking}")
            ```
        """
        url = f"{self.base_path}/{channel_id}/set-engagement-tracking"
        response = await self._session.post(url, json={"enable": enable})
        return cast(
            EmailChannel,
            self.create_resource(response.json(), is_partial=False),
        )
