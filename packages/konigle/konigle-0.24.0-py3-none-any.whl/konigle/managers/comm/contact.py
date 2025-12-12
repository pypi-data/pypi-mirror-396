"""
Contact managers for the Konigle SDK.

This module provides managers for contact resources, enabling
contact management operations including CRUD operations and filtering.
"""

from typing import cast

from konigle.filters.comm import ContactFilters
from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.comm.contact import (
    Contact,
    ContactCreate,
    ContactUpdate,
    ContactUpdateLTV,
)


class BaseContactManager:
    """Base class for contact managers with shared configuration."""

    resource_class = Contact
    """The resource model class this manager handles."""

    resource_update_class = ContactUpdate
    """The model class used for updating resources."""

    filter_class = ContactFilters
    """The filter model class for this resource type."""

    base_path = "/reachout/api/v1/contacts"
    """The API base path for this resource type."""


class ContactManager(BaseContactManager, BaseSyncManager):
    """Synchronous manager for contact resources."""

    def create(self, data: ContactCreate) -> Contact:
        """
        Create a new contact.

        Args:
            data: Contact creation data including all required fields

        Returns:
            Created contact instance with Active Record capabilities

        Example:
            ```python
            from konigle.models.comm import (
                ContactCreate,
                MarketingConsent,
            )

            contact_data = ContactCreate(
                email="john@example.com",
                first_name="John",
                last_name="Doe",
                phone="+1234567890",
                source="lead",
                tags=["newsletter", "webinar"],
                marketing_consent=MarketingConsent(
                    email=True,
                    sms=False,
                    whatsapp=True,
                ),
            )
            contact = client.contacts.create(contact_data)
            print(f"Created contact: {contact.email}")
            ```
        """
        return cast(Contact, super().create(data))

    def update_ltv(self, data: ContactUpdateLTV) -> Contact:
        """
        Update contact LTV (Lifetime Value) from a purchase.

        Adds revenue to a contact's lifetime value based on email
        address. This is a non-detail interface that doesn't require
        a contact ID.

        Args:
            data: LTV update data including email, value, and currency

        Returns:
            Updated contact with new LTV

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            from konigle.models.comm import ContactUpdateLTV
            from decimal import Decimal

            ltv_data = ContactUpdateLTV(
                email="customer@example.com",
                value=Decimal("149.99"),
                currency="USD",
            )
            contact = client.contacts.update_ltv(ltv_data)
            print(f"Contact LTV: {contact.ltv} {contact.ltv_currency}")
            ```
        """
        url = f"{self.base_path}/update-ltv"
        response = self._session.post(
            url, json=data.model_dump(exclude_none=True, exclude_unset=True)
        )
        return cast(Contact, self.create_resource(response.json()))


class AsyncContactManager(BaseContactManager, BaseAsyncManager):
    """Asynchronous manager for contact resources."""

    async def create(self, data: ContactCreate) -> Contact:
        """
        Create a new contact.

        Args:
            data: Contact creation data including all required fields

        Returns:
            Created contact instance with Active Record capabilities

        Example:
            ```python
            from konigle.models.comm import (
                ContactCreate,
                MarketingConsent,
            )

            contact_data = ContactCreate(
                email="john@example.com",
                first_name="John",
                last_name="Doe",
                phone="+1234567890",
                source="lead",
                tags=["newsletter", "webinar"],
                marketing_consent=MarketingConsent(
                    email=True,
                    sms=False,
                    whatsapp=True,
                ),
            )
            contact = await client.contacts.create(contact_data)
            print(f"Created contact: {contact.email}")
            ```
        """
        return cast(Contact, await super().create(data))

    async def update_ltv(self, data: ContactUpdateLTV) -> Contact:
        """
        Update contact LTV (Lifetime Value) from a purchase.

        Adds revenue to a contact's lifetime value based on email
        address. This is a non-detail interface that doesn't require
        a contact ID.

        Args:
            data: LTV update data including email, value, and currency

        Returns:
            Updated contact with new LTV

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            from konigle.models.comm import ContactUpdateLTV
            from decimal import Decimal

            ltv_data = ContactUpdateLTV(
                email="customer@example.com",
                value=Decimal("149.99"),
                currency="USD",
            )
            contact = await client.contacts.update_ltv(ltv_data)
            print(f"Contact LTV: {contact.ltv} {contact.ltv_currency}")
            ```
        """
        url = f"{self.base_path}/update-ltv"
        response = await self._session.post(
            url, json=data.model_dump(exclude_none=True, exclude_unset=True)
        )
        return cast(Contact, self.create_resource(response.json()))
