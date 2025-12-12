"""
Media asset managers for the Konigle SDK.

This module provides managers for Image, Video, and Document assets.
All three types use the same backend endpoint but are differentiated
by mime_type filtering.
"""

from typing import cast

from konigle.filters.core import DocumentFilters, ImageFilters, VideoFilters
from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.core.media_asset import (
    Document,
    DocumentCreate,
    DocumentUpdate,
    Image,
    ImageCreate,
    ImageGenerate,
    ImageUpdate,
    Video,
    VideoCreate,
    VideoUpdate,
)
from konigle.types.common import PaginatedResponse, PaginationParams
from konigle.utils import model_to_dict


class BaseImageManager:
    resource_class = Image
    """The resource model class this manager handles."""

    resource_update_class = ImageUpdate
    """The resource update model class this manager handles."""

    base_path = "/admin/api/storefront-assets"
    """The API base path for this resource type."""

    filter_class = ImageFilters
    """The filter model class for this resource type."""


class ImageManager(BaseImageManager, BaseSyncManager):
    """Manager for image assets."""

    def create(self, data: ImageCreate) -> Image:
        """Create a new image asset."""
        return cast(Image, super().create(data))

    def update(self, id_: str, data: ImageUpdate) -> Image:
        """Update an existing image asset."""
        return cast(Image, super().update(id_, data))

    def generate(self, data: ImageGenerate) -> Image:
        """
        Generate an image from a text prompt.

        Args:
            data: Image generation parameters including prompt and options

        Returns:
            Generated image asset
        """
        data_dict = self._model_to_dict(data)
        response = self._session.post(
            f"{self._get_base_url()}/generate-image", json=data_dict
        )
        return cast(Image, self.create_resource(response.json()))

    def search(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse[Image]:
        """
        Search for images by a text query.

        Args:
            query: The search query string.
            page: The page number for pagination.
            page_size: The number of items per page.
        Returns:
            List of image assets matching the query.
        """
        params = {
            "q": query,
            "asset_type": "image",
            "page": page,
            "page_size": page_size,
        }

        response = self._session.get(f"{self.base_path}/search", params=params)
        data = response.json()
        return cast(
            PaginatedResponse[Image],
            self._create_paginated_response(
                data,
                pagination=PaginationParams(page=page, page_size=page_size),
            ),
        )


class BaseVideoManager:
    resource_class = Video
    """The resource model class this manager handles."""

    resource_update_class = VideoUpdate
    """The resource update model class this manager handles."""

    base_path = "/admin/api/storefront-assets"
    """The API base path for this resource type."""

    filter_class = VideoFilters
    """The filter model class for this resource type."""


class VideoManager(BaseVideoManager, BaseSyncManager):
    """Manager for video assets."""

    def create(self, data: VideoCreate) -> Video:
        """Create a new video asset."""
        return cast(Video, super().create(data))

    def update(self, id_: str, data: VideoUpdate) -> Video:
        """Update an existing video asset."""
        return cast(Video, super().update(id_, data))

    def search(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse[Video]:
        """
        Search for videos by a text query.

        Args:
            query: The search query string.
            page: The page number for pagination.
            page_size: The number of items per page.
        Returns:
            List of video assets matching the query.
        """
        params = {
            "q": query,
            "asset_type": "video",
            "page": page,
            "page_size": page_size,
        }
        response = self._session.get(f"{self.base_path}/search", params=params)
        data = response.json()
        return cast(
            PaginatedResponse[Video],
            self._create_paginated_response(
                data,
                pagination=PaginationParams(page=page, page_size=page_size),
            ),
        )


class BaseDocumentManager:
    resource_class = Document
    """The resource model class this manager handles."""

    resource_update_class = DocumentUpdate
    """The resource update model class this manager handles."""

    base_path = "/admin/api/admin/api/storefront-assets"
    """The API base path for this resource type."""

    filter_class = DocumentFilters
    """The filter model class for this resource type."""


class DocumentManager(BaseDocumentManager, BaseSyncManager):
    """Manager for document assets."""

    def create(self, data: DocumentCreate) -> Document:
        """Create a new document asset."""
        return cast(Document, super().create(data))

    def update(self, id_: str, data: DocumentUpdate) -> Document:
        """Update an existing document asset."""
        return cast(Document, super().update(id_, data))

    def search(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse[Document]:
        """
        Search for documents by a text query.

        Args:
            query: The search query string.
            page: The page number for pagination.
            page_size: The number of items per page.
        Returns:
            List of document assets matching the query.
        """
        params = {
            "q": query,
            "asset_type": "document",
            "page": page,
            "page_size": page_size,
        }
        response = self._session.get(f"{self.base_path}/search", params=params)
        data = response.json()
        return cast(
            PaginatedResponse[Document],
            self._create_paginated_response(
                data,
                pagination=PaginationParams(page=page, page_size=page_size),
            ),
        )


# Async managers
class AsyncImageManager(BaseImageManager, BaseAsyncManager):
    """Async manager for image assets."""

    async def create(self, data: ImageCreate) -> Image:
        """Create a new image asset."""
        return cast(Image, await super().create(data))

    async def update(self, id_: str, data: ImageUpdate) -> Image:
        """Update an existing image asset."""
        return cast(Image, await super().update(id_, data))

    async def generate(self, data: ImageGenerate) -> Image:
        """
        Generate an image from a text prompt.

        Args:
            data: Image generation parameters including prompt and options

        Returns:
            Generated image asset
        """
        data_dict = model_to_dict(data)
        response = await self._session.post(
            f"{self._get_base_url()}/generate-image", json=data_dict
        )
        return cast(Image, self.create_resource(response.json()))

    async def search(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse[Image]:
        """
        Search for images by a text query.

        Args:
            query: The search query string.
            page: The page number for pagination.
            page_size: The number of items per page.
        Returns:
            List of image assets matching the query.
        """
        params = {
            "q": query,
            "asset_type": "image",
            "page": page,
            "page_size": page_size,
        }
        response = await self._session.get(
            f"{self.base_path}/search", params=params
        )
        data = response.json()
        return cast(
            PaginatedResponse[Image],
            self._create_paginated_response(
                data,
                pagination=PaginationParams(page=page, page_size=page_size),
            ),
        )


class AsyncVideoManager(BaseVideoManager, BaseAsyncManager):
    """Async manager for video assets."""

    async def create(self, data: VideoCreate) -> Video:
        """Create a new video asset."""
        return cast(Video, await super().create(data))

    async def update(self, id_: str, data: VideoUpdate) -> Video:
        """Update an existing video asset."""
        return cast(Video, await super().update(id_, data))

    async def search(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse[Video]:
        """
        Search for videos by a text query.

        Args:
            query: The search query string.
            page: The page number for pagination.
            page_size: The number of items per page.
        Returns:
            List of video assets matching the query.
        """
        params = {
            "q": query,
            "asset_type": "video",
            "page": page,
            "page_size": page_size,
        }
        response = await self._session.get(
            f"{self.base_path}/search", params=params
        )
        data = response.json()
        return cast(
            PaginatedResponse[Video],
            self._create_paginated_response(
                data,
                pagination=PaginationParams(page=page, page_size=page_size),
            ),
        )


class AsyncDocumentManager(BaseDocumentManager, BaseAsyncManager):
    """Async manager for document assets."""

    async def create(self, data: DocumentCreate) -> Document:
        """Create a new document asset."""
        return cast(Document, await super().create(data))

    async def update(self, id_: str, data: DocumentUpdate) -> Document:
        """Update an existing document asset."""
        return cast(Document, await super().update(id_, data))

    async def search(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse[Document]:
        """
        Search for documents by a text query.

        Args:
            query: The search query string.
            page: The page number for pagination.
            page_size: The number of items per page.
        Returns:
            List of document assets matching the query.
        """
        params = {
            "q": query,
            "asset_type": "document",
            "page": page,
            "page_size": page_size,
        }
        response = await self._session.get(
            f"{self.base_path}/search", params=params
        )
        data = response.json()
        return cast(
            PaginatedResponse[Document],
            self._create_paginated_response(
                data,
                pagination=PaginationParams(page=page, page_size=page_size),
            ),
        )
