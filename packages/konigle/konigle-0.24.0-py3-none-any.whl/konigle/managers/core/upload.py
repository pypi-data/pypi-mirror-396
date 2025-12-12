"""
Upload managers for the Konigle SDK.

This module provides managers for Upload resources with specialized
methods for handling file uploads without update capability.
"""

from typing import Any, Dict, Optional, cast

from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.core.upload import Upload, UploadCreate


class BaseUploadManager:
    resource_class = Upload
    """The resource model class this manager handles."""

    resource_update_class = None
    """No update capability for uploads."""

    base_path = "/admin/api/uploads"
    """The API base path for this resource type."""

    filter_class = None
    """No filtering for uploads."""


class UploadManager(BaseUploadManager, BaseSyncManager):
    """Manager for upload resources."""

    def create(self, data: UploadCreate) -> Upload:
        """Create a new upload."""
        return cast(Upload, super().create(data))

    def update(self, id_: str, data: Any) -> None:
        """Update operation not supported for uploads."""
        raise NotImplementedError("Upload resources cannot be updated")

    def create_cloud_upload(
        self,
        mime_type: str,
        file_size: int,
        filename: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a presigned upload URL for direct to cloud upload.

        Args:
            mime_type: MIME type of the file to upload
            file_size: Size of the file in bytes
            filename: Name of the file
            name: Display name for the upload (optional)

        Returns:
            Upload info with presigned URL details
        """
        data = {
            "mime_type": mime_type,
            "file_size": file_size,
            "filename": filename,
        }
        if name:
            data["name"] = name

        response = self._session.post(
            f"{self._get_base_url()}/create-cloud-upload", json=data
        )
        return response.json()

    def mark_started(self, id_: str) -> Upload:
        """
        Mark the upload as started.

        This is called for direct to cloud uploads once the upload is started.

        Args:
            id_: Upload ID

        Returns:
            Updated upload instance
        """
        response = self._session.post(f"{self._get_detail_url(id_)}/mark-started")
        return cast(Upload, self.create_resource(response.json()))

    def mark_completed(self, id_: str) -> Upload:
        """
        Mark the upload as completed.

        This is called for direct to cloud uploads once the upload is completed.

        Args:
            id_: Upload ID

        Returns:
            Updated upload instance
        """
        response = self._session.post(f"{self._get_detail_url(id_)}/mark-completed")
        return cast(Upload, self.create_resource(response.json()))

    def mark_failed(self, id_: str) -> Upload:
        """
        Mark the upload as failed.

        This is called for direct to cloud uploads if the upload fails.

        Args:
            id_: Upload ID

        Returns:
            Updated upload instance
        """
        response = self._session.post(f"{self._get_detail_url(id_)}/mark-failed")
        return cast(Upload, self.create_resource(response.json()))


class AsyncUploadManager(BaseUploadManager, BaseAsyncManager):
    """Async manager for upload resources."""

    async def create(self, data: UploadCreate) -> Upload:
        """Create a new upload."""
        return cast(Upload, await super().create(data))

    async def update(self, id_: str, data: Any) -> None:
        """Update operation not supported for uploads."""
        raise NotImplementedError("Upload resources cannot be updated")

    async def create_cloud_upload(
        self,
        mime_type: str,
        file_size: int,
        filename: str,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a presigned upload URL for direct to cloud upload.

        Args:
            mime_type: MIME type of the file to upload
            file_size: Size of the file in bytes
            filename: Name of the file
            name: Display name for the upload (optional)

        Returns:
            Upload info with presigned URL details
        """
        data = {
            "mime_type": mime_type,
            "file_size": file_size,
            "filename": filename,
        }
        if name:
            data["name"] = name

        response = await self._session.post(
            f"{self._get_base_url()}/create-cloud-upload", json=data
        )
        return response.json()

    async def mark_started(self, id_: str) -> Upload:
        """
        Mark the upload as started.

        This is called for direct to cloud uploads once the upload is started.

        Args:
            id_: Upload ID

        Returns:
            Updated upload instance
        """
        response = await self._session.post(
            f"{self._get_detail_url(id_)}/mark-started"
        )
        return cast(Upload, self.create_resource(response.json()))

    async def mark_completed(self, id_: str) -> Upload:
        """
        Mark the upload as completed.

        This is called for direct to cloud uploads once the upload is completed.

        Args:
            id_: Upload ID

        Returns:
            Updated upload instance
        """
        response = await self._session.post(
            f"{self._get_detail_url(id_)}/mark-completed"
        )
        return cast(Upload, self.create_resource(response.json()))

    async def mark_failed(self, id_: str) -> Upload:
        """
        Mark the upload as failed.

        This is called for direct to cloud uploads if the upload fails.

        Args:
            id_: Upload ID

        Returns:
            Updated upload instance
        """
        response = await self._session.post(
            f"{self._get_detail_url(id_)}/mark-failed"
        )
        return cast(Upload, self.create_resource(response.json()))