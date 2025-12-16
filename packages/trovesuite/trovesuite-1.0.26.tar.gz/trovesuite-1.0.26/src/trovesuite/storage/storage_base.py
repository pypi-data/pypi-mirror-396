from typing import Optional
from pydantic import BaseModel


class StorageConnectionBase(BaseModel):
    """Base model for Azure Storage connection using Managed Identity"""
    storage_account_url: str  # e.g., https://<account-name>.blob.core.windows.net
    container_name: str
    managed_identity_client_id: Optional[str] = None  # Optional: For user-assigned managed identity


class StorageFileUploadBase(BaseModel):
    """Base model for file upload operations"""
    storage_account_url: str
    container_name: str
    file_content: bytes
    blob_name: str
    directory_path: Optional[str] = None
    content_type: Optional[str] = None
    managed_identity_client_id: Optional[str] = None


class StorageFileUpdateBase(BaseModel):
    """Base model for file update operations"""
    storage_account_url: str
    container_name: str
    blob_name: str
    file_content: bytes
    content_type: Optional[str] = None
    managed_identity_client_id: Optional[str] = None


class StorageFileDeleteBase(BaseModel):
    """Base model for file delete operations"""
    storage_account_url: str
    container_name: str
    blob_name: str
    managed_identity_client_id: Optional[str] = None


class StorageFileDownloadBase(BaseModel):
    """Base model for file download operations"""
    storage_account_url: str
    container_name: str
    blob_name: str
    managed_identity_client_id: Optional[str] = None


class StorageFileUrlBase(BaseModel):
    """Base model for getting presigned URL"""
    storage_account_url: str
    container_name: str
    blob_name: str
    expiry_hours: Optional[int] = 1
    managed_identity_client_id: Optional[str] = None


class StorageContainerCreateBase(BaseModel):
    """Base model for creating a container"""
    storage_account_url: str
    container_name: str
    public_access: Optional[str] = None
    managed_identity_client_id: Optional[str] = None
