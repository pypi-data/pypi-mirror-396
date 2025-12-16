from pydantic import BaseModel
from typing import Optional


# Container Creation

class StorageContainerCreateControllerReadDto(BaseModel):
    container_name: str
    container_url: Optional[str] = None


class StorageContainerCreateServiceReadDto(StorageContainerCreateControllerReadDto):
    pass


# File Upload

class StorageFileUploadControllerReadDto(BaseModel):
    blob_name: str
    blob_url: str
    content_type: Optional[str] = None
    size: Optional[int] = None


class StorageFileUploadServiceReadDto(StorageFileUploadControllerReadDto):
    pass


# File Update

class StorageFileUpdateControllerReadDto(BaseModel):
    blob_name: str
    blob_url: str
    updated_at: Optional[str] = None


class StorageFileUpdateServiceReadDto(StorageFileUpdateControllerReadDto):
    pass


# File Delete

class StorageFileDeleteControllerReadDto(BaseModel):
    blob_name: str
    deleted: bool


class StorageFileDeleteServiceReadDto(StorageFileDeleteControllerReadDto):
    pass


# File Download

class StorageFileDownloadControllerReadDto(BaseModel):
    blob_name: str
    content: bytes
    content_type: Optional[str] = None
    size: Optional[int] = None


class StorageFileDownloadServiceReadDto(StorageFileDownloadControllerReadDto):
    pass


# File URL

class StorageFileUrlControllerReadDto(BaseModel):
    blob_name: str
    presigned_url: str
    expires_in_hours: int


class StorageFileUrlServiceReadDto(StorageFileUrlControllerReadDto):
    pass
