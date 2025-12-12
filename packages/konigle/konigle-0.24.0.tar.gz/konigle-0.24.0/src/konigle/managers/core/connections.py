"""
Connection managers for the Konigle SDK.

This module provides managers for third-party API connection resources,
enabling listing and retrieval of connection details and credentials.
"""

from typing import Dict, cast

from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.core.connections import Connection


class BaseConnectionManager:
    """Base configuration for Connection resource managers."""

    resource_class = Connection
    """The resource model class this manager handles."""

    base_path = "/relay/api/v1/connections"
    """The API base path for this resource type."""


class ConnectionManager(BaseConnectionManager, BaseSyncManager):
    """Manager for connection resources."""

    def get(self, id_: str) -> Connection:
        """Get a specific connection by ID."""
        raise NotImplementedError(
            "Getting a specific connection by ID is not supported via SDK. "
            "Use the Konigle admin interface to view connection details."
        )

    def get_credentials(self, provider: str) -> Dict[str, str]:
        """
        Get connection credentials by ID.

        Returns the raw credentials dictionary for the connection,
        which may include sensitive information like tokens.

        Args:
            provider: Connection provider code

        Returns:
            Dictionary containing connection credentials
        """
        path = f"{self.base_path}/get-credentials"
        response = self._session.get(path, params={"provider": provider})
        return response.json()

    def create(self, *args, **kwargs):
        """Creation not supported via SDK."""
        raise NotImplementedError(
            "Creating connections is not supported via SDK. "
            "Use the Konigle admin interface to set up new connections."
        )

    def update(self, *args, **kwargs):
        """Update not supported via SDK."""
        raise NotImplementedError(
            "Updating connections is not supported via SDK. "
            "Use the Konigle admin interface to manage connections."
        )

    def delete(self, *args, **kwargs):
        """Deletion not supported via SDK."""
        raise NotImplementedError(
            "Deleting connections is not supported via SDK. "
            "Use the Konigle admin interface to manage connections."
        )


class AsyncConnectionManager(BaseConnectionManager, BaseAsyncManager):
    """Async manager for connection resources."""

    async def get(self, id_: str) -> Connection:
        """Get a specific connection by ID."""
        raise NotImplementedError(
            "Getting a specific connection by ID is not supported via SDK. "
            "Use the Konigle admin interface to view connection details."
        )

    async def get_credentials(self, provider: str) -> Dict[str, str]:
        """
        Get connection credentials by ID.

        Returns the raw credentials dictionary for the connection,
        which may include sensitive information like tokens.

        Args:
            provider: Connection provider code
        Returns:
            Dictionary containing connection credentials
        """
        path = f"{self.base_path}/get-credentials"
        response = await self._session.get(path, params={"provider": provider})
        return response.json()

    async def create(self, *args, **kwargs):
        """Creation not supported via SDK."""
        raise NotImplementedError(
            "Creating connections is not supported via SDK. "
            "Use the Konigle admin interface to set up new connections."
        )

    async def update(self, *args, **kwargs):
        """Update not supported via SDK."""
        raise NotImplementedError(
            "Updating connections is not supported via SDK. "
            "Use the Konigle admin interface to manage connections."
        )

    async def delete(self, *args, **kwargs):
        """Deletion not supported via SDK."""
        raise NotImplementedError(
            "Deleting connections is not supported via SDK. "
            "Use the Konigle admin interface to manage connections."
        )
