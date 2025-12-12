"""
Folder managers for the Konigle SDK.

This module provides managers for folder resources, enabling hierarchical
content organization and management.
"""

from typing import cast

from konigle.filters.website import FolderFilters
from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.website.folder import Folder, FolderCreate, FolderUpdate


class BaseFolderManager:
    resource_class = Folder
    """The resource model class this manager handles."""

    resource_update_class = FolderUpdate
    """The model class used for updating resources."""

    base_path = "/admin/api/content-folders"
    """The API base path for this resource type."""

    filter_class = FolderFilters
    """The filter model class for this resource type."""


class FolderManager(BaseFolderManager, BaseSyncManager):
    """Manager for folder resources."""

    def create(self, data: FolderCreate) -> Folder:
        """Create a new folder."""
        return cast(Folder, super().create(data))

    def update(self, id_: str, data: FolderUpdate) -> Folder:
        """Update an existing folder."""
        return cast(Folder, super().update(id_, data))

    def get(self, id_: str) -> Folder:
        return cast(Folder, super().get(id_))

    def publish(self, id_: str) -> Folder:
        """Publish a folder."""
        path = f"{self.base_path}/{id_}/publish"
        response = self._session.post(path)
        return cast(
            Folder, self.create_resource(response.json(), is_partial=False)
        )

    def unpublish(self, id_: str) -> Folder:
        """Unpublish a folder."""
        path = f"{self.base_path}/{id_}/unpublish"
        response = self._session.post(path)
        return cast(
            Folder, self.create_resource(response.json(), is_partial=False)
        )

    def change_handle(
        self, id_: str, new_handle: str, redirect: bool = False
    ) -> Folder:
        """Change the handle of a folder."""

        path = f"{self.base_path}/{id_}/change-handle"
        response = self._session.post(
            path, json={"handle": new_handle, "redirect": redirect}
        )
        return cast(
            Folder, self.create_resource(response.json(), is_partial=False)
        )

    def get_crawler_view(self, id_: str) -> str:
        """Get the crawler view of a folder."""
        path = f"{self.base_path}/{id_}/crawler-view"
        response = self._session.get(path)
        return response.text

    def get_home_folder(self, detail: bool = False) -> Folder | None:
        """Get the home folder."""

        response = self.list(
            folder_type="home",
            is_original_version=True,
        )
        if response.payload:
            folder = cast(Folder, response.payload[0])
            if detail:
                folder.load_detail()
            return folder
        return None


class AsyncFolderManager(BaseFolderManager, BaseAsyncManager):
    """Async manager for folder resources."""

    async def create(self, data: FolderCreate) -> Folder:
        """Create a new folder."""
        return cast(Folder, await super().create(data))

    async def update(self, id_: str, data: FolderUpdate) -> Folder:
        """Update an existing folder."""
        return cast(Folder, await super().update(id_, data))

    async def get(self, id_: str) -> Folder:
        return cast(Folder, await super().get(id_))

    async def publish(self, id_: str) -> Folder:
        """Publish a folder."""
        path = f"{self.base_path}/{id_}/publish"
        response = await self._session.post(path)
        return cast(
            Folder, self.create_resource(response.json(), is_partial=False)
        )

    async def unpublish(self, id_: str) -> Folder:
        """Unpublish a folder."""
        path = f"{self.base_path}/{id_}/unpublish"
        response = await self._session.post(path)
        return cast(
            Folder, self.create_resource(response.json(), is_partial=False)
        )

    async def change_handle(
        self, id_: str, new_handle: str, redirect: bool = False
    ) -> Folder:
        """Change the handle of a folder."""

        path = f"{self.base_path}/{id_}/change-handle"
        response = await self._session.post(
            path, json={"handle": new_handle, "redirect": redirect}
        )
        return cast(
            Folder, self.create_resource(response.json(), is_partial=False)
        )

    async def get_crawler_view(self, id_: str) -> str:
        """Get the crawler view of a folder."""
        path = f"{self.base_path}/{id_}/crawler-view"
        response = await self._session.get(path)
        return response.text

    async def get_home_folder(self, detail: bool = False) -> Folder | None:
        """Get the home folder."""

        response = await self.list(
            folder_type="home",
            is_original_version=True,
        )
        if response.payload:
            folder = cast(Folder, response.payload[0])
            if detail:
                await folder.aload_detail()
            return folder
        return None
