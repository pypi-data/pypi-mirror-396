"""
Campaign managers for the Konigle SDK.

This module provides managers for campaign resources, enabling
campaign management operations including CRUD and execution control.
"""

from typing import Optional, cast

from konigle.filters.comm import CampaignFilters
from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.comm.campaign import (
    Campaign,
    CampaignAddLTV,
    CampaignCreate,
    CampaignCreateEmail,
    CampaignUpdate,
)
from konigle.utils import model_to_dict


class BaseCampaignManager:
    """Base class for campaign managers with shared configuration."""

    resource_class = Campaign
    """The resource model class this manager handles."""

    resource_update_class = CampaignUpdate
    """The model class used for updating resources."""

    filter_class = CampaignFilters
    """The filter model class for this resource type."""

    base_path = "/reachout/api/v1/campaigns"
    """The API base path for this resource type."""


class CampaignManager(BaseCampaignManager, BaseSyncManager):
    """Synchronous manager for campaign resources."""

    def create(self, data: CampaignCreate) -> Campaign:
        """
        Create a new campaign.

        Args:
            data: Campaign creation data including all required fields

        Returns:
            Created campaign instance with Active Record capabilities

        Example:
            ```python
            from konigle.models.comm import CampaignCreate

            campaign_data = CampaignCreate(
                name="Summer Sale 2024",
                channel_type="email",
                email_channel="channel_id",
                email_template="template_id",
                audience="audience_id",
                description="Promotional campaign for summer sale",
                scheduled_at=None,  # Send immediately
                execution_duration_minutes=60,  # Spread over 1 hour
                utm_code="summer-sale-2024",
            )
            campaign = client.campaigns.create(campaign_data)
            print(f"Created campaign: {campaign.name}")
            ```
        """
        return cast(Campaign, super().create(data))

    def start(self, campaign_id: str) -> Campaign:
        """
        Start a campaign. Only works when status is draft or scheduled.

        Args:
            campaign_id: ID of the campaign to start

        Returns:
            Updated campaign with new status

        Raises:
            ValueError: If campaign is not in draft or scheduled status
            APIError: If the API request fails

        Example:
            ```python
            campaign = client.campaigns.start("campaign_id")
            print(f"Campaign started: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/start"
        response = self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    def pause(self, campaign_id: str) -> Campaign:
        """
        Pause a running campaign. Only works when status is running.

        Args:
            campaign_id: ID of the campaign to pause

        Returns:
            Updated campaign with paused status

        Raises:
            ValueError: If campaign is not in running status
            APIError: If the API request fails

        Example:
            ```python
            campaign = client.campaigns.pause("campaign_id")
            print(f"Campaign paused: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/pause"
        response = self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    def resume(self, campaign_id: str) -> Campaign:
        """
        Resume a paused campaign. Only works when status is paused.

        Args:
            campaign_id: ID of the campaign to resume

        Returns:
            Updated campaign with resumed status

        Raises:
            ValueError: If campaign is not in paused status
            APIError: If the API request fails

        Example:
            ```python
            campaign = client.campaigns.resume("campaign_id")
            print(f"Campaign resumed: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/resume"
        response = self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    def cancel(self, campaign_id: str) -> Campaign:
        """
        Cancel a campaign. Works when status is running, draft, scheduled or
        paused.

        Args:
            campaign_id: ID of the campaign to cancel

        Returns:
            Updated campaign with cancelled status

        Raises:
            ValueError: If campaign cannot be cancelled
            APIError: If the API request fails

        Example:
            ```python
            campaign = client.campaigns.cancel("campaign_id")
            print(f"Campaign cancelled: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/cancel"
        response = self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    def schedule(
        self, campaign_id: str, scheduled_at: Optional[str]
    ) -> Campaign:
        """
        Schedule or reschedule a campaign.

        Args:
            campaign_id: ID of the campaign to schedule
            scheduled_at: ISO 8601 datetime string for when to send the campaign.
                          None is allowd if the scheduled_at is already set.
        Returns:
            Updated campaign with new scheduled time
        Raises:
            ValueError: If campaign is not in draft status
            APIError: If the API request fails
        """
        url = f"{self.base_path}/{campaign_id}/schedule"
        payload = {}
        if scheduled_at is not None:
            payload["scheduled_at"] = scheduled_at
        response = self._session.post(url, json=payload)
        return cast(Campaign, self.create_resource(response.json()))

    def add_ltv(self, campaign_id: str, data: CampaignAddLTV) -> Campaign:
        """
        Add LTV (Lifetime Value) to a campaign from a purchase.

        Records revenue generated from a contact's purchase and updates
        both the campaign and contact LTV values.

        Args:
            campaign_id: ID of the campaign to add LTV to
            data: LTV data including contact email, value, and currency

        Returns:
            Updated campaign with new LTV

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            from konigle.models.comm import CampaignAddLTV
            from decimal import Decimal

            ltv_data = CampaignAddLTV(
                contact_email="customer@example.com",
                value=Decimal("99.99"),
                currency="USD",
            )
            campaign = client.campaigns.add_ltv("campaign_id", ltv_data)
            print(f"Campaign LTV: {campaign.ltv} {campaign.ltv_currency}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/add-ltv"
        response = self._session.post(
            url, json=data.model_dump(exclude_none=True, exclude_unset=True)
        )
        return cast(Campaign, self.create_resource(response.json()))

    def new_email_campaign(self, data: CampaignCreateEmail) -> Campaign:
        """
        Create a new email campaign with audience and template.

        This hybrid API creates a campaign along with its associated
        audience and email template in a single operation.

        Args:
            data: Email campaign data with all required fields

        Returns:
            Created campaign instance

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            from konigle.models.comm import CampaignCreateEmail

            campaign_data = CampaignCreateEmail(
                campaign_name="Summer Sale 2024",
                email_channel="marketing",
                contact_tags=["newsletter", "vip"],
                subject="Summer Sale - 50% Off!",
                body_html="<h1>Limited Time Offer!</h1>",
                body_text="Summer Sale - 50% Off!",
                utm_code="summer-sale-2024",
            )
            campaign = client.campaigns.new_email_campaign(campaign_data)
            print(f"Created campaign: {campaign.name}")
            ```
        """
        url = f"{self.base_path}/new-email-campaign"

        response = self._session.post(url, json=model_to_dict(data))
        result = response.json()
        return cast(Campaign, self.create_resource(result.get("campaign", {})))

    def send_test_email(self, campaign_id: str, email_address: str) -> dict:
        """
        Send a test email for the specified email campaign.

        Args:
            campaign_id: ID of the email campaign to send a test for
            email_address: Recipient email address for the test email
        Returns:
            dict: API response indicating success or failure
        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_path}/{campaign_id}/send-test-email"
        payload = {"email_address": email_address}
        response = self._session.post(url, json=payload)
        return response.json()


class AsyncCampaignManager(BaseCampaignManager, BaseAsyncManager):
    """Asynchronous manager for campaign resources."""

    async def create(self, data: CampaignCreate) -> Campaign:
        """
        Create a new campaign.

        Args:
            data: Campaign creation data including all required fields

        Returns:
            Created campaign instance with Active Record capabilities

        Example:
            ```python
            from konigle.models.comm import CampaignCreate

            campaign_data = CampaignCreate(
                name="Summer Sale 2024",
                channel_type="email",
                email_channel="channel_id",
                email_template="template_id",
                audience="audience_id",
                description="Promotional campaign for summer sale",
                scheduled_at=None,  # Send immediately
                execution_duration_minutes=60,  # Spread over 1 hour
                utm_code="summer-sale-2024",
            )
            campaign = await client.campaigns.create(campaign_data)
            print(f"Created campaign: {campaign.name}")
            ```
        """
        return cast(Campaign, await super().create(data))

    async def start(self, campaign_id: str) -> Campaign:
        """
        Start a campaign. Only works when status is draft or scheduled.

        Args:
            campaign_id: ID of the campaign to start

        Returns:
            Updated campaign with new status

        Raises:
            ValueError: If campaign is not in draft or scheduled status
            APIError: If the API request fails

        Example:
            ```python
            campaign = await client.campaigns.start("campaign_id")
            print(f"Campaign started: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/start"
        response = await self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    async def pause(self, campaign_id: str) -> Campaign:
        """
        Pause a running campaign. Only works when status is running.

        Args:
            campaign_id: ID of the campaign to pause

        Returns:
            Updated campaign with paused status

        Raises:
            ValueError: If campaign is not in running status
            APIError: If the API request fails

        Example:
            ```python
            campaign = await client.campaigns.pause("campaign_id")
            print(f"Campaign paused: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/pause"
        response = await self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    async def resume(self, campaign_id: str) -> Campaign:
        """
        Resume a paused campaign. Only works when status is paused.

        Args:
            campaign_id: ID of the campaign to resume

        Returns:
            Updated campaign with resumed status

        Raises:
            ValueError: If campaign is not in paused status
            APIError: If the API request fails

        Example:
            ```python
            campaign = await client.campaigns.resume("campaign_id")
            print(f"Campaign resumed: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/resume"
        response = await self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    async def cancel(self, campaign_id: str) -> Campaign:
        """
        Cancel a campaign. Works when status is running, draft, or
        scheduled.

        Args:
            campaign_id: ID of the campaign to cancel

        Returns:
            Updated campaign with cancelled status

        Raises:
            ValueError: If campaign cannot be cancelled
            APIError: If the API request fails

        Example:
            ```python
            campaign = await client.campaigns.cancel("campaign_id")
            print(f"Campaign cancelled: {campaign.status}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/cancel"
        response = await self._session.post(url)
        return cast(Campaign, self.create_resource(response.json()))

    async def schedule(
        self, campaign_id: str, scheduled_at: Optional[str]
    ) -> Campaign:
        """
        Schedule or reschedule a campaign.
        Args:
            campaign_id: ID of the campaign to schedule
            scheduled_at: ISO 8601 datetime string for when to send the campaign.
                          None is allowd if the scheduled_at is already set.
        Returns:
            Updated campaign with new scheduled time
        Raises:
            ValueError: If campaign is not in draft status
            APIError: If the API request fails
        """
        url = f"{self.base_path}/{campaign_id}/schedule"
        payload = {}
        if scheduled_at is not None:
            payload["scheduled_at"] = scheduled_at
        response = await self._session.post(url, json=payload)
        return cast(Campaign, self.create_resource(response.json()))

    async def add_ltv(
        self, campaign_id: str, data: CampaignAddLTV
    ) -> Campaign:
        """
        Add LTV (Lifetime Value) to a campaign from a purchase.

        Records revenue generated from a contact's purchase and updates
        both the campaign and contact LTV values.

        Args:
            campaign_id: ID of the campaign to add LTV to
            data: LTV data including contact email, value, and currency

        Returns:
            Updated campaign with new LTV

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            from konigle.models.comm import CampaignAddLTV
            from decimal import Decimal

            ltv_data = CampaignAddLTV(
                contact_email="customer@example.com",
                value=Decimal("99.99"),
                currency="USD",
            )
            campaign = await client.campaigns.add_ltv(
                "campaign_id", ltv_data
            )
            print(f"Campaign LTV: {campaign.ltv} {campaign.ltv_currency}")
            ```
        """
        url = f"{self.base_path}/{campaign_id}/add-ltv"
        response = await self._session.post(
            url, json=data.model_dump(exclude_none=True, exclude_unset=True)
        )
        return cast(Campaign, self.create_resource(response.json()))

    async def new_email_campaign(self, data: CampaignCreateEmail) -> Campaign:
        """
        Create a new email campaign with audience and template.

        This hybrid API creates a campaign along with its associated
        audience and email template in a single operation.

        Args:
            data: Email campaign data with all required fields

        Returns:
            Created campaign instance

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            from konigle.models.comm import CampaignCreateEmail

            campaign_data = CampaignCreateEmail(
                campaign_name="Summer Sale 2024",
                email_channel="marketing",
                contact_tags=["newsletter", "vip"],
                subject="Summer Sale - 50% Off!",
                body_html="<h1>Limited Time Offer!</h1>",
                body_text="Summer Sale - 50% Off!",
                utm_code="summer-sale-2024",
            )
            campaign = await client.campaigns.new_email_campaign(
                campaign_data
            )
            print(f"Created campaign: {campaign.name}")
            ```
        """
        url = f"{self.base_path}/new-email-campaign"
        response = await self._session.post(url, json=model_to_dict(data))
        result = response.json()
        return cast(Campaign, self.create_resource(result.get("campaign", {})))

    async def send_test_email(
        self, campaign_id: str, email_address: str
    ) -> dict:
        """
        Send a test email for the specified email campaign.

        Args:
            campaign_id: ID of the email campaign to send a test for
            email_address: Recipient email address for the test email
        Returns:
            dict: API response indicating success or failure
        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_path}/{campaign_id}/send-test-email"
        payload = {"email_address": email_address}
        response = await self._session.post(url, json=payload)
        return response.json()
