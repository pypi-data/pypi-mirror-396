"""
Connection models for the Konigle SDK.

This module provides models for third-party API integrations and connections
including OAuth and API key based connections.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field

from konigle.models.base import TimestampedResource


class ConnectionStatus(str, Enum):
    """Status of a connection."""

    ACTIVE = "active"
    """Connection is active and working."""

    INACTIVE = "inactive"
    """Connection is inactive."""

    INVALID = "invalid"
    """Connection credentials are invalid."""


class Connection(TimestampedResource):
    """
    Connection resource model.

    Represents a third-party API integration connection with OAuth or API key
    authentication. Connections are site-specific and store credentials,
    tokens, and metadata for external service integrations.
    """

    provider: str = Field(
        ...,
        title="Provider Code",
        description="Provider code identifying the third-party service.",
    )
    """Provider code identifying the third-party service."""

    token_expires_at: Optional[datetime] = Field(
        default=None,
        title="Token Expiry",
        description="Expiration timestamp for the access token.",
    )
    """Expiration timestamp for the access token."""

    status: ConnectionStatus = Field(
        default=ConnectionStatus.ACTIVE,
        title="Connection Status",
        description="Current status of the connection.",
    )
    """Current status of the connection."""

    root_resource_id: Optional[str] = Field(
        default=None,
        title="Root Resource ID",
        description="Authorized resource ID (e.g., account ID, email).",
    )
    """Authorized resource ID (e.g., account ID, email)."""

    root_resource_name: Optional[str] = Field(
        default=None,
        title="Root Resource Name",
        description="Authorized resource name (e.g., account name).",
    )
    """Authorized resource name (e.g., account name)."""

    scopes: List[str] = Field(
        default_factory=list,
        title="OAuth Scopes",
        description="List of OAuth scopes authorized for this connection.",
    )
    """List of OAuth scopes authorized for this connection."""

    def __str__(self) -> str:
        return (
            f"Connection(id = {self.id}, provider = {self.provider}, "
            f"status={self.status})"
        )


__all__ = [
    "Connection",
]
