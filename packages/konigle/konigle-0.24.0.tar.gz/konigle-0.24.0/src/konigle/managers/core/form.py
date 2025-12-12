"""
Form managers for the Konigle SDK.

This module provides managers for Form resources from the forms service.
Forms are accessed through a separate service at forms.konigle.com
requiring Bearer token authentication.
"""

from pprint import pp
from typing import TYPE_CHECKING, Dict, Optional, Union, cast

from konigle.config import ClientConfig
from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.base import CreateModel
from konigle.models.core.form import Form, FormCreate, FormSubmission
from konigle.session import AsyncSession, SyncSession
from konigle.types.common import PaginatedResponse, PaginationParams
from konigle.utils import model_to_dict

if TYPE_CHECKING:
    from konigle.managers.core.connections import (
        AsyncConnectionManager,
        ConnectionManager,
    )


class BaseFormManager:
    """Base configuration for Form resource managers."""

    resource_class = Form
    """The resource model class this manager handles."""

    base_path = "/api/dev/forms/"
    """The API base path for this resource type."""

    forms_base_url = "https://forms.konigle.com"
    """The base URL for the forms service."""

    forms_connection_provider = "konigle_forms"
    """The connection provider code for forms service."""

    def _get_create_url(self) -> str:
        """Get the URL for creating forms."""
        return self.base_path

    def _get_submissions_url(self, slug: str) -> str:
        """Get the URL for listing form submissions."""
        return f"{self.base_path}{slug}/submissions/"

    def _get_detail_url(self, slug: str) -> str:
        """Get the URL for retrieving a specific form."""
        return f"{self.base_path}{slug}/"

    def set_connection_manager(
        self,
        connection_manager: Union[
            "ConnectionManager", "AsyncConnectionManager"
        ],
    ):
        """
        Set the connection manager for fetching credentials.

        Args:
            connection_manager: Connection manager instance
        """
        self._connection_manager = connection_manager

    def _create_forms_config(
        self, access_token: str, sdk_session_config: ClientConfig
    ) -> ClientConfig:
        """
        Create ClientConfig for forms service.

        Args:
            access_token: Bearer token for forms service

        Returns:
            ClientConfig configured for forms service
        """
        config_data = sdk_session_config.model_dump()
        config_data["base_url"] = self.forms_base_url
        config_data["auth_prefix"] = "Bearer"
        config_data["api_key"] = access_token
        return ClientConfig(**config_data)

    def _normalize_forms_response(self, data: Dict, page_size: int) -> Dict:
        """
        Normalize forms service response to match SDK format.

        Args:
            data: Response data from forms service
            page_size: Number of items per page

        Returns:
            Normalized response data
        """
        count = data.get("count", 0)
        if page_size > 0:
            num_pages = (count + page_size - 1) // page_size
        else:
            num_pages = 1
        return {
            "count": data.get("count", 0),
            "results": data.get("results", []),
            "num_pages": num_pages,
            "next": data.get("next"),
            "previous": data.get("previous"),
        }


class FormManager(BaseFormManager, BaseSyncManager):
    """Manager for form resources."""

    def __init__(self, session: "SyncSession"):
        super().__init__(session)
        self._connection_manager: Optional["ConnectionManager"] = None
        self._forms_session: Optional[SyncSession] = None

    def _get_forms_session(self) -> SyncSession:
        """
        Get or create a session for the forms service.

        Returns:
            Session configured for forms service with Bearer auth
        """
        if self._forms_session is None:
            # Get credentials from connection manager
            if not self._connection_manager:
                raise ValueError(
                    "Connection manager not set. "
                    "Use set_connection_manager() first."
                )
            credentials = self._connection_manager.get_credentials(
                self.forms_connection_provider
            )
            access_token = credentials.get("access_token")
            if not access_token:
                raise ValueError(
                    "No access_token found in konigle_forms credentials"
                )

            # Create config and session for forms service
            forms_config = self._create_forms_config(
                access_token, self._session.config
            )
            self._forms_session = SyncSession(forms_config)

        return self._forms_session

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[Form]:
        """
        List forms with pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            **filter_kwargs: Filter arguments as keyword arguments

        Returns:
            Paginated response containing list of forms
        """
        # Get forms service session
        forms_session = self._get_forms_session()

        # Build request parameters
        params = {
            "page": page,
            "page_size": page_size,
        }

        # Make request to forms service
        response = forms_session.get(self.base_path, params=params)
        data = response.json()

        # Normalize response format
        normalized_data = self._normalize_forms_response(data, page_size)

        # Create paginated response
        pagination = PaginationParams(page=page, page_size=page_size)
        return cast(
            PaginatedResponse[Form],
            self._create_paginated_response(normalized_data, pagination),
        )

    def create(self, data: Union[FormCreate, Dict[str, str]]) -> Form:
        """
        Create a new form.

        Args:
            data: Form creation data

        Returns:
            Created form instance
        """
        # Get forms service session
        forms_session = self._get_forms_session()

        # Convert data to dict
        if isinstance(data, CreateModel):
            data_dict = model_to_dict(data)
        else:
            data_dict = {k: v for k, v in data.items() if v is not None}

        # Make request to forms service
        response = forms_session.post(self._get_create_url(), json=data_dict)
        form_data = response.json()

        # the creation does not return the full form data, so fetch it again.
        return self.get(form_data["slug"])

    def get(self, slug: str) -> Form:
        """Get a specific form by slug"""
        forms_session = self._get_forms_session()
        response = forms_session.get(self._get_detail_url(slug))
        return cast(Form, self.create_resource(response.json()))

    def list_submissions(
        self,
        slug: str,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[FormSubmission]:
        """
        List submissions for a specific form.

        Args:
            slug: Form slug
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Paginated response containing list of form submissions
        """
        # Get forms service session
        forms_session = self._get_forms_session()

        # Build request parameters
        params = {
            "page": page,
            "page_size": page_size,
        }

        # Make request to forms service
        response = forms_session.get(
            self._get_submissions_url(slug), params=params
        )
        data = response.json()

        # Normalize response format
        normalized_data = self._normalize_forms_response(data, page_size)

        # Create FormSubmission instances
        submissions = [
            FormSubmission.model_validate(item)
            for item in normalized_data.get("results", [])
        ]

        # Create paginated response
        return PaginatedResponse[FormSubmission](
            payload=submissions,
            count=normalized_data.get("count", 0),
            next=normalized_data.get("next"),
            previous=normalized_data.get("previous"),
            page_size=page_size,
            current_page=page,
            num_pages=normalized_data.get("num_pages", 1),
        )

    def update(self, *args, **kwargs):  # type: ignore
        """Update not supported."""
        raise NotImplementedError("Updating forms is not yet supported.")

    def delete(self, *args, **kwargs):  # type: ignore
        """Deletion not supported."""
        raise NotImplementedError("Deleting forms is not yet supported.")


class AsyncFormManager(BaseFormManager, BaseAsyncManager):
    """Async manager for form resources."""

    def __init__(self, session: "AsyncSession"):
        super().__init__(session)
        self._connection_manager: Optional["AsyncConnectionManager"] = None
        self._forms_session: Optional[AsyncSession] = None

    async def _get_forms_session(self) -> AsyncSession:
        """
        Get or create a session for the forms service.

        Returns:
            Session configured for forms service with Bearer auth
        """
        if self._forms_session is None:
            # Get credentials from connection manager
            if not self._connection_manager:
                raise ValueError(
                    "Connection manager not set. "
                    "Use set_connection_manager() first."
                )
            credentials = await self._connection_manager.get_credentials(
                "konigle_forms"
            )
            access_token = credentials.get("access_token")
            if not access_token:
                raise ValueError(
                    "No access_token found in konigle_forms credentials"
                )

            # Create config and session for forms service
            forms_config = self._create_forms_config(
                access_token, self._session.config
            )
            self._forms_session = AsyncSession(forms_config)

        return self._forms_session

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[Form]:
        """
        List forms with pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            **filter_kwargs: Filter arguments as keyword arguments

        Returns:
            Paginated response containing list of forms
        """
        # Get forms service session
        forms_session = await self._get_forms_session()

        # Build request parameters
        params = {
            "page": page,
            "page_size": page_size,
        }

        # Make request to forms service
        response = await forms_session.get(self.base_path, params=params)
        data = response.json()

        # Normalize response format
        normalized_data = self._normalize_forms_response(data, page_size)

        # Create paginated response
        pagination = PaginationParams(page=page, page_size=page_size)
        return cast(
            PaginatedResponse[Form],
            self._create_paginated_response(normalized_data, pagination),
        )

    async def create(self, data: Union[FormCreate, Dict[str, str]]) -> Form:
        """
        Create a new form.

        Args:
            data: Form creation data

        Returns:
            Created form instance
        """
        # Get forms service session
        forms_session = await self._get_forms_session()

        # Convert data to dict
        if isinstance(data, CreateModel):
            data_dict = model_to_dict(data)
        else:
            data_dict = {k: v for k, v in data.items() if v is not None}

        # Make request to forms service
        response = await forms_session.post(
            self._get_create_url(), json=data_dict
        )
        form_data = response.json()
        # the creation does not return the full form data, so fetch it again.
        return await self.get(form_data["slug"])

    async def get(self, slug: str) -> Form:  # type: ignore
        """Get a specific form by slug"""
        forms_session = await self._get_forms_session()
        response = await forms_session.get(self._get_detail_url(slug))
        return cast(Form, self.create_resource(response.json()))

    async def list_submissions(
        self,
        slug: str,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[FormSubmission]:
        """
        List submissions for a specific form.

        Args:
            slug: Form slug
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Paginated response containing list of form submissions
        """
        # Get forms service session
        forms_session = await self._get_forms_session()

        # Build request parameters
        params = {
            "page": page,
            "page_size": page_size,
        }

        # Make request to forms service
        response = await forms_session.get(
            self._get_submissions_url(slug), params=params
        )
        data = response.json()

        # Normalize response format
        normalized_data = self._normalize_forms_response(data, page_size)

        # Create FormSubmission instances
        submissions = [
            FormSubmission.model_validate(item)
            for item in normalized_data.get("results", [])
        ]

        # Create paginated response
        return PaginatedResponse[FormSubmission](
            payload=submissions,
            count=normalized_data.get("count", 0),
            next=normalized_data.get("next"),
            previous=normalized_data.get("previous"),
            page_size=page_size,
            current_page=page,
            num_pages=normalized_data.get("num_pages", 1),
        )

    async def update(self, *args, **kwargs):  # type: ignore
        """Update not supported."""
        raise NotImplementedError("Updating forms is not yet supported.")

    async def delete(self, *args, **kwargs):  # type: ignore
        """Deletion not supported."""
        raise NotImplementedError("Deleting forms is not yet supported.")


__all__ = [
    "FormManager",
    "AsyncFormManager",
]
