"""
TroveSuite Storage Service

Provides Azure Storage blob management capabilities for TroveSuite applications.
Includes container creation, file upload/download/update/delete, and presigned URL generation.
"""

from .storage_service import StorageService
from .storage_write_dto import (
    StorageContainerCreateServiceWriteDto,
    StorageFileUploadServiceWriteDto,
    StorageFileUpdateServiceWriteDto,
    StorageFileDeleteServiceWriteDto,
    StorageFileDownloadServiceWriteDto,
    StorageFileUrlServiceWriteDto
)
from .storage_read_dto import (
    StorageContainerCreateServiceReadDto,
    StorageFileUploadServiceReadDto,
    StorageFileUpdateServiceReadDto,
    StorageFileDeleteServiceReadDto,
    StorageFileDownloadServiceReadDto,
    StorageFileUrlServiceReadDto
)

__all__ = [
    "StorageService",
    # Write DTOs
    "StorageContainerCreateServiceWriteDto",
    "StorageFileUploadServiceWriteDto",
    "StorageFileUpdateServiceWriteDto",
    "StorageFileDeleteServiceWriteDto",
    "StorageFileDownloadServiceWriteDto",
    "StorageFileUrlServiceWriteDto",
    # Read DTOs
    "StorageContainerCreateServiceReadDto",
    "StorageFileUploadServiceReadDto",
    "StorageFileUpdateServiceReadDto",
    "StorageFileDeleteServiceReadDto",
    "StorageFileDownloadServiceReadDto",
    "StorageFileUrlServiceReadDto",
]
