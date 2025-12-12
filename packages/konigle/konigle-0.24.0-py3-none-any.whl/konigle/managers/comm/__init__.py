"""
Communication managers for the Konigle SDK.

This module provides manager classes for email, SMS, WhatsApp, and other
communication channels supported by the Konigle platform.
"""

from .audience import AsyncAudienceManager, AudienceManager
from .campaign import *
from .contact import AsyncContactManager, ContactManager
from .email import *

__all__ = [
    # Audience managers
    "AudienceManager",
    "AsyncAudienceManager",
    # Campaign managers
    "CampaignManager",
    "AsyncCampaignManager",
    # Contact managers
    "ContactManager",
    "AsyncContactManager",
    # Email managers
    "EmailAccountManager",
    "AsyncEmailAccountManager",
    "EmailChannelManager",
    "AsyncEmailChannelManager",
    "EmailIdentityManager",
    "AsyncEmailIdentityManager",
]
