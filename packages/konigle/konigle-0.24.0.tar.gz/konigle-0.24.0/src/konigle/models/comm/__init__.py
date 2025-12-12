"""
Communication models for the Konigle SDK.

This module provides models for email, SMS, WhatsApp, and other
communication channels supported by the Konigle platform.
"""

from .audience import Audience, AudienceCreate, AudienceUpdate
from .campaign import (
    Campaign,
    CampaignAddLTV,
    CampaignChannelType,
    CampaignCreate,
    CampaignCreateEmail,
    CampaignExecution,
    CampaignExecutionStatus,
    CampaignStatus,
    CampaignUpdate,
)
from .contact import (
    Contact,
    ContactCreate,
    ContactSource,
    ContactUpdate,
    ContactUpdateLTV,
    MarketingConsent,
)
from .email import *  # noqa

__all__ = [
    # Audience models
    "Audience",
    "AudienceCreate",
    "AudienceUpdate",
    # Campaign models
    "Campaign",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignExecution",
    "CampaignAddLTV",
    "CampaignCreateEmail",
    "CampaignChannelType",
    "CampaignStatus",
    "CampaignExecutionStatus",
    # Contact models
    "Contact",
    "ContactCreate",
    "ContactUpdate",
    "ContactUpdateLTV",
    "MarketingConsent",
    "ContactSource",
    # Email models
    "EmailAccount",
    "EmailAccountCreate",
    "EmailAccountUpdate",
    "EmailAccountSetup",
    "EmailChannel",
    "EmailChannelCreate",
    "EmailChannelUpdate",
    "EmailIdentity",
    "EmailIdentityCreate",
    "EmailIdentityUpdate",
    "EmailTemplate",
    "EmailTemplateCreate",
    "EmailTemplateUpdate",
    # Enums
    "EmailChannelType",
    "EmailChannelStatus",
    "EmailIdentityType",
    "EmailVerificationStatus",
    # Send models
    "Email",
    "EmailResponse",
]
