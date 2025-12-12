"""
Upload models for the Konigle SDK.

This module defines models for file uploads - general purpose private
file uploads that represent temporary uploads for files in the Konigle
platform. These differ from StorefrontAsset as they are not used
directly in the site but contribute to site storage.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field, field_validator, model_validator

from konigle.models.base import CreateModel, Resource
from konigle.types.common import FileInputT
from konigle.utils import FileInput


class UploadStatus(str, Enum):
    """Upload status enumeration."""

    PENDING = "pending"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class Upload(Resource):
    """Upload model for general purpose file uploads."""

    url: Optional[str] = Field(
        ..., title="File URL", description="URL to access the uploaded file"
    )
    """URL to access the uploaded file"""

    mime_type: str = Field(
        ...,
        max_length=100,
        title="MIME Type",
        description="MIME type of the uploaded file",
    )
    """MIME type of the uploaded file"""

    name: str = Field(
        default="",
        max_length=255,
        title="Name",
        description="Name of the file for display and search purposes",
    )
    """Name of the file for display and search purposes"""

    size: int = Field(
        default=0,
        ge=0,
        title="Size",
        description="Size of the file in bytes",
    )
    """Size of the file in bytes"""

    meta: dict = Field(
        default_factory=dict,
        title="Metadata",
        description="Additional metadata such as width, height for images",
    )
    """Additional metadata such as width, height for images"""

    description: str = Field(
        default="",
        max_length=1000,
        title="Description",
        description="Optional description of the upload",
    )
    """Optional description of the upload"""

    created_at: datetime = Field(
        ..., title="Created At", description="Creation timestamp."
    )
    """Creation timestamp."""

    storage_path: str = Field(
        default="",
        max_length=500,
        title="Storage Path",
        description="Object key or path in the storage backend",
    )
    """Object key or path in the storage backend"""

    etag: str = Field(
        default="",
        max_length=64,
        title="ETag",
        description="ETag or checksum of the file content",
    )
    """ETag or checksum of the file content"""

    status: UploadStatus = Field(
        default=UploadStatus.COMPLETED,
        title="Status",
        description="Status of the upload",
    )
    """Status of the upload"""

    upload_started_at: Optional[str] = Field(
        None,
        title="Upload Started At",
        description="Timestamp when the upload started",
    )
    """Timestamp when the upload started"""

    upload_ended_at: Optional[str] = Field(
        None,
        title="Upload Ended At",
        description="Timestamp when the upload ended",
    )
    """Timestamp when the upload ended"""

    tags: List[str] = Field(
        default_factory=list,
        title="Tags",
        description="Tags for categorization",
    )
    """Tags for categorization"""

    def __str__(self) -> str:
        return f"Upload(id = {self.id}, name = {self.name}, url = {self.url})"


class UploadCreate(CreateModel):
    """Create model for file uploads."""

    file: FileInputT = Field(
        ...,
        title="File",
        description="File to upload. Can be file path, bytes, "
        "BytesIO, BinaryIO, or tuple of (file_data, filename)",
    )
    """File to upload. Can be file path, bytes, BytesIO, BinaryIO, or
    tuple of (file_data, filename)"""

    name: str = Field(
        default="",
        max_length=255,
        title="Name",
        description="Name of the file for display and search purposes",
    )
    """Name of the file for display and search purposes"""

    tags: str = Field(
        default="",
        title="Tags",
        description="Tags for categorization. Comma-separated string.",
    )
    """Tags for categorization. Comma-separated string."""

    meta: Optional[dict] = Field(
        default=None,
        title="Meta",
        description="Optional metadata dictionary",
    )
    """Optional metadata dictionary"""

    description: Optional[str] = Field(
        default=None,
        title="Description",
        description="Optional description of the upload",
    )
    """Optional description of the upload"""

    @field_validator("file")
    @classmethod
    def validate_file(cls, v):
        """Ensure we're uploading a supported file type."""
        supported_extensions = [
            ".pdf",
            ".csv",
            ".txt",
            ".png",
            ".jpeg",
            ".jpg",
            ".gif",
            ".webp",
            ".svg",
            ".zip",
            ".doc",
            ".docx",
        ]

        # Handle tuple input
        if isinstance(v, tuple) and len(v) == 2:
            _, filename = v
            if not any(
                filename.lower().endswith(ext) for ext in supported_extensions
            ):
                raise ValueError(
                    f"File must be a supported type: "
                    f"{', '.join(supported_extensions)}"
                )
        elif isinstance(v, str) and not v.startswith("https://"):
            if not any(
                v.lower().endswith(ext) for ext in supported_extensions
            ):
                raise ValueError(
                    f"File must be a supported type: "
                    f"{', '.join(supported_extensions)}"
                )
        return v

    @model_validator(mode="after")
    def normalize_file(self):
        """Convert file paths or bytes to FileInput."""
        self.file = FileInput.normalize(self.file)
        return self


__all__ = [
    "Upload",
    "UploadCreate",
    "UploadStatus",
]
