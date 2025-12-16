from typing import List
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from io import BytesIO
from .storage_write_dto import (
    StorageContainerCreateControllerWriteDto,
    StorageFileUploadControllerWriteDto,
    StorageFileUpdateControllerWriteDto,
    StorageFileDeleteControllerWriteDto,
    StorageFileDownloadControllerWriteDto,
    StorageFileUrlControllerWriteDto
)
from .storage_read_dto import (
    StorageContainerCreateControllerReadDto,
    StorageFileUploadControllerReadDto,
    StorageFileUpdateControllerReadDto,
    StorageFileDeleteControllerReadDto,
    StorageFileDownloadControllerReadDto,
    StorageFileUrlControllerReadDto
)
from .storage_service import StorageService
from ..entities.sh_response import Respons

storage_router = APIRouter(tags=["File Storage"])


@storage_router.post("/create-container", response_model=Respons[StorageContainerCreateControllerReadDto])
async def create_container(data: StorageContainerCreateControllerWriteDto):
    """
    Create a new Azure Storage container.

    Example request body:
    {
        "storage_account_url": "https://myaccount.blob.core.windows.net",
        "container_name": "my-container",
        "public_access": null,
        "managed_identity_client_id": "your-client-id"  // optional
    }
    """
    return StorageService.create_container(data=data)


@storage_router.post("/upload", response_model=Respons[StorageFileUploadControllerReadDto])
async def upload_file(
    storage_account_url: str = Form(...),
    container_name: str = Form(...),
    blob_name: str = Form(...),
    file: UploadFile = File(...),
    directory_path: str = Form(None),
    managed_identity_client_id: str = Form(None)
):
    """
    Upload a file to Azure Storage.

    Use form-data with the following fields:
    - storage_account_url: Your Azure storage URL
    - container_name: Container name
    - blob_name: Name for the blob
    - file: The file to upload
    - directory_path: Optional directory path (e.g., "uploads/2024")
    - managed_identity_client_id: Optional client ID for user-assigned managed identity
    """
    content = await file.read()

    upload_data = StorageFileUploadControllerWriteDto(
        storage_account_url=storage_account_url,
        container_name=container_name,
        file_content=content,
        blob_name=blob_name,
        directory_path=directory_path,
        content_type=file.content_type,
        managed_identity_client_id=managed_identity_client_id
    )

    return StorageService.upload_file(data=upload_data)


@storage_router.put("/update", response_model=Respons[StorageFileUpdateControllerReadDto])
async def update_file(
    storage_account_url: str = Form(...),
    container_name: str = Form(...),
    blob_name: str = Form(...),
    file: UploadFile = File(...),
    managed_identity_client_id: str = Form(None)
):
    """
    Update an existing file in Azure Storage.

    Use form-data with the following fields:
    - storage_account_url: Your Azure storage URL
    - container_name: Container name
    - blob_name: Full blob name including path (e.g., "uploads/2024/file.pdf")
    - file: The new file content
    - managed_identity_client_id: Optional client ID for user-assigned managed identity
    """
    content = await file.read()

    update_data = StorageFileUpdateControllerWriteDto(
        storage_account_url=storage_account_url,
        container_name=container_name,
        blob_name=blob_name,
        file_content=content,
        content_type=file.content_type,
        managed_identity_client_id=managed_identity_client_id
    )

    return StorageService.update_file(data=update_data)


@storage_router.delete("/delete", response_model=Respons[StorageFileDeleteControllerReadDto])
async def delete_file(data: StorageFileDeleteControllerWriteDto):
    """
    Delete a file from Azure Storage.

    Example request body:
    {
        "storage_account_url": "https://myaccount.blob.core.windows.net",
        "container_name": "my-container",
        "blob_name": "uploads/2024/file.pdf",
        "managed_identity_client_id": "your-client-id"  // optional
    }
    """
    return StorageService.delete_file(data=data)


@storage_router.delete("/delete-multiple", response_model=Respons[StorageFileDeleteControllerReadDto])
async def delete_multiple_files(
    storage_account_url: str,
    container_name: str,
    blob_names: List[str],
    managed_identity_client_id: str = None
):
    """
    Delete multiple files from Azure Storage.

    Example request body:
    {
        "storage_account_url": "https://myaccount.blob.core.windows.net",
        "container_name": "my-container",
        "blob_names": ["file1.pdf", "file2.pdf", "folder/file3.jpg"],
        "managed_identity_client_id": "your-client-id"  // optional
    }
    """
    return StorageService.delete_multiple_files(
        storage_account_url=storage_account_url,
        container_name=container_name,
        blob_names=blob_names,
        managed_identity_client_id=managed_identity_client_id
    )


@storage_router.post("/download")
async def download_file(data: StorageFileDownloadControllerWriteDto):
    """
    Download a file from Azure Storage.

    Returns the file as a streaming response.

    Example request body:
    {
        "storage_account_url": "https://myaccount.blob.core.windows.net",
        "container_name": "my-container",
        "blob_name": "uploads/2024/file.pdf",
        "managed_identity_client_id": "your-client-id"  // optional
    }
    """
    result = StorageService.download_file(data=data)

    if not result.success:
        return result

    file_data = result.data[0]

    # Return as streaming response
    return StreamingResponse(
        BytesIO(file_data.content),
        media_type=file_data.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={data.blob_name.split('/')[-1]}"
        }
    )


@storage_router.post("/get-url", response_model=Respons[StorageFileUrlControllerReadDto])
async def get_file_url(data: StorageFileUrlControllerWriteDto):
    """
    Generate a presigned URL for a file.

    Example request body:
    {
        "storage_account_url": "https://myaccount.blob.core.windows.net",
        "container_name": "my-container",
        "blob_name": "uploads/2024/file.pdf",
        "expiry_hours": 2,
        "managed_identity_client_id": "your-client-id"  // optional
    }
    """
    return StorageService.get_file_url(data=data)
