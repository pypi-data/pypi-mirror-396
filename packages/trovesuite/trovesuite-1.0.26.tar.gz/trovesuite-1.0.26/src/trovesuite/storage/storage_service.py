from datetime import datetime, timedelta
from typing import List
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from ..entities.sh_response import Respons
from .storage_read_dto import (
    StorageContainerCreateServiceReadDto,
    StorageFileUploadServiceReadDto,
    StorageFileUpdateServiceReadDto,
    StorageFileDeleteServiceReadDto,
    StorageFileDownloadServiceReadDto,
    StorageFileUrlServiceReadDto
)
from .storage_write_dto import (
    StorageContainerCreateServiceWriteDto,
    StorageFileUploadServiceWriteDto,
    StorageFileUpdateServiceWriteDto,
    StorageFileDeleteServiceWriteDto,
    StorageFileDownloadServiceWriteDto,
    StorageFileUrlServiceWriteDto
)


class StorageService:
    """
    Azure Storage service for managing blob storage operations using Managed Identity authentication.
    Supports both system-assigned and user-assigned managed identities.
    """

    @staticmethod
    def _get_credential(managed_identity_client_id: str = None):
        """
        Get Azure credential for authentication.
        - Tries Managed Identity (for Azure environments)
        - Falls back to DefaultAzureCredential (for local dev)
        """
        try:
            if managed_identity_client_id:
                return ManagedIdentityCredential(client_id=managed_identity_client_id)
            else:
                return DefaultAzureCredential(exclude_managed_identity_credential=True)
            
        except Exception:

            # Always fallback to DefaultAzureCredential
            return DefaultAzureCredential(exclude_managed_identity_credential=True)


    @staticmethod
    def _get_blob_service_client(storage_account_url: str, managed_identity_client_id: str = None) -> BlobServiceClient:
        """
        Create a BlobServiceClient using Managed Identity.

        Args:
            storage_account_url: Azure Storage account URL (e.g., https://myaccount.blob.core.windows.net)
            managed_identity_client_id: Optional client ID for user-assigned managed identity

        Returns:
            BlobServiceClient instance
        """
        credential = StorageService._get_credential(managed_identity_client_id)
        return BlobServiceClient(account_url=storage_account_url, credential=credential)

    @staticmethod
    def create_container(data: StorageContainerCreateServiceWriteDto) -> Respons[StorageContainerCreateServiceReadDto]:
        """
        Create a new Azure Storage container.

        Args:
            data: Container creation parameters including storage account URL and container name

        Returns:
            Response object containing container details or error information
        """
        try:
            blob_service_client = StorageService._get_blob_service_client(
                data.storage_account_url,
                data.managed_identity_client_id
            )
            container_client = blob_service_client.create_container(
                name=data.container_name,
                public_access=data.public_access
            )

            container_url = container_client.url

            result = StorageContainerCreateServiceReadDto(
                container_name=data.container_name,
                container_url=container_url
            )

            return Respons[StorageContainerCreateServiceReadDto](
                detail=f"Container '{data.container_name}' created successfully",
                error=None,
                data=[result],
                status_code=201,
                success=True,
            )

        except ResourceExistsError:
            return Respons[StorageContainerCreateServiceReadDto](
                detail=f"Container '{data.container_name}' already exists",
                error="Resource already exists",
                data=[],
                status_code=409,
                success=False,
            )
        except Exception as e:
            return Respons[StorageContainerCreateServiceReadDto](
                detail="Failed to create container",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )

    @staticmethod
    def upload_file(data: StorageFileUploadServiceWriteDto) -> Respons[StorageFileUploadServiceReadDto]:
        """
        Upload a file to Azure Storage blob container.

        Args:
            data: File upload parameters including storage account URL, container name,
                  file content, blob name, and optional directory path

        Returns:
            Response object containing uploaded file details or error information
        """
        try:
            # Construct the full blob name with directory path if provided
            blob_name = data.blob_name
            if data.directory_path:
                # Ensure directory path ends with / and doesn't start with /
                dir_path = data.directory_path.strip('/')
                blob_name = f"{dir_path}/{blob_name}"

            blob_service_client = StorageService._get_blob_service_client(
                data.storage_account_url,
                data.managed_identity_client_id
            )
            blob_client = blob_service_client.get_blob_client(
                container=data.container_name,
                blob=blob_name
            )

            # Upload the file
            content_settings = None
            if data.content_type:
                from azure.storage.blob import ContentSettings
                content_settings = ContentSettings(content_type=data.content_type)

            blob_client.upload_blob(
                data.file_content,
                overwrite=False,
                content_settings=content_settings
            )

            # Get blob properties
            properties = blob_client.get_blob_properties()

            result = StorageFileUploadServiceReadDto(
                blob_name=blob_name,
                blob_url=blob_client.url,
                content_type=properties.content_settings.content_type if properties.content_settings else None,
                size=properties.size
            )

            return Respons[StorageFileUploadServiceReadDto](
                detail=f"File '{blob_name}' uploaded successfully",
                error=None,
                data=[result],
                status_code=201,
                success=True,
            )

        except ResourceExistsError:
            return Respons[StorageFileUploadServiceReadDto](
                detail=f"File '{blob_name}' already exists",
                error="Resource already exists. Use update_file to modify existing files.",
                data=[],
                status_code=409,
                success=False,
            )
        except Exception as e:
            return Respons[StorageFileUploadServiceReadDto](
                detail="Failed to upload file",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )

    @staticmethod
    def update_file(data: StorageFileUpdateServiceWriteDto) -> Respons[StorageFileUpdateServiceReadDto]:
        """
        Update an existing file in Azure Storage blob container.

        Args:
            data: File update parameters including storage account URL, container name,
                  blob name, and new file content

        Returns:
            Response object containing updated file details or error information
        """
        try:
            blob_service_client = StorageService._get_blob_service_client(
                data.storage_account_url,
                data.managed_identity_client_id
            )
            blob_client = blob_service_client.get_blob_client(
                container=data.container_name,
                blob=data.blob_name
            )

            # Upload with overwrite=True to update
            content_settings = None
            if data.content_type:
                from azure.storage.blob import ContentSettings
                content_settings = ContentSettings(content_type=data.content_type)

            blob_client.upload_blob(
                data.file_content,
                overwrite=True,
                content_settings=content_settings
            )

            # Get updated properties
            properties = blob_client.get_blob_properties()

            result = StorageFileUpdateServiceReadDto(
                blob_name=data.blob_name,
                blob_url=blob_client.url,
                updated_at=properties.last_modified.isoformat() if properties.last_modified else None
            )

            return Respons[StorageFileUpdateServiceReadDto](
                detail=f"File '{data.blob_name}' updated successfully",
                error=None,
                data=[result],
                status_code=200,
                success=True,
            )

        except ResourceNotFoundError:
            return Respons[StorageFileUpdateServiceReadDto](
                detail=f"File '{data.blob_name}' not found",
                error="Resource not found. Use upload_file to create new files.",
                data=[],
                status_code=404,
                success=False,
            )
        except Exception as e:
            return Respons[StorageFileUpdateServiceReadDto](
                detail="Failed to update file",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )

    @staticmethod
    def delete_file(data: StorageFileDeleteServiceWriteDto) -> Respons[StorageFileDeleteServiceReadDto]:
        """
        Delete a file from Azure Storage blob container.

        Args:
            data: File delete parameters including storage account URL, container name,
                  and blob name

        Returns:
            Response object containing deletion status or error information
        """
        try:
            blob_service_client = StorageService._get_blob_service_client(
                data.storage_account_url,
                data.managed_identity_client_id
            )
            blob_client = blob_service_client.get_blob_client(
                container=data.container_name,
                blob=data.blob_name
            )

            # Delete the blob
            blob_client.delete_blob()

            result = StorageFileDeleteServiceReadDto(
                blob_name=data.blob_name,
                deleted=True
            )

            return Respons[StorageFileDeleteServiceReadDto](
                detail=f"File '{data.blob_name}' deleted successfully",
                error=None,
                data=[result],
                status_code=200,
                success=True,
            )

        except ResourceNotFoundError:
            return Respons[StorageFileDeleteServiceReadDto](
                detail=f"File '{data.blob_name}' not found",
                error="Resource not found",
                data=[],
                status_code=404,
                success=False,
            )
        except Exception as e:
            return Respons[StorageFileDeleteServiceReadDto](
                detail="Failed to delete file",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )

    @staticmethod
    def delete_multiple_files(
        storage_account_url: str,
        container_name: str,
        blob_names: List[str],
        managed_identity_client_id: str = None
    ) -> Respons[StorageFileDeleteServiceReadDto]:
        """
        Delete multiple files from Azure Storage blob container.

        Args:
            storage_account_url: Azure Storage account URL
            container_name: Name of the container
            blob_names: List of blob names to delete
            managed_identity_client_id: Optional client ID for user-assigned managed identity

        Returns:
            Response object containing deletion status for all files
        """
        try:
            blob_service_client = StorageService._get_blob_service_client(
                storage_account_url,
                managed_identity_client_id
            )
            container_client = blob_service_client.get_container_client(container_name)

            results = []
            errors = []

            for blob_name in blob_names:
                try:
                    blob_client = container_client.get_blob_client(blob_name)
                    blob_client.delete_blob()
                    results.append(StorageFileDeleteServiceReadDto(
                        blob_name=blob_name,
                        deleted=True
                    ))
                except ResourceNotFoundError:
                    errors.append(f"File '{blob_name}' not found")
                except Exception as e:
                    errors.append(f"Failed to delete '{blob_name}': {str(e)}")

            if errors and not results:
                return Respons[StorageFileDeleteServiceReadDto](
                    detail="Failed to delete any files",
                    error="; ".join(errors),
                    data=[],
                    status_code=500,
                    success=False,
                )
            elif errors:
                return Respons[StorageFileDeleteServiceReadDto](
                    detail=f"Deleted {len(results)} file(s) with {len(errors)} error(s)",
                    error="; ".join(errors),
                    data=results,
                    status_code=207,  # Multi-Status
                    success=True,
                )
            else:
                return Respons[StorageFileDeleteServiceReadDto](
                    detail=f"Successfully deleted {len(results)} file(s)",
                    error=None,
                    data=results,
                    status_code=200,
                    success=True,
                )

        except Exception as e:
            return Respons[StorageFileDeleteServiceReadDto](
                detail="Failed to delete files",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )

    @staticmethod
    def download_file(data: StorageFileDownloadServiceWriteDto) -> Respons[StorageFileDownloadServiceReadDto]:
        """
        Download a file from Azure Storage blob container.

        Args:
            data: File download parameters including storage account URL, container name,
                  and blob name

        Returns:
            Response object containing file content and metadata or error information
        """
        try:
            blob_service_client = StorageService._get_blob_service_client(
                data.storage_account_url,
                data.managed_identity_client_id
            )
            blob_client = blob_service_client.get_blob_client(
                container=data.container_name,
                blob=data.blob_name
            )

            # Download the blob
            download_stream = blob_client.download_blob()
            file_content = download_stream.readall()

            # Get blob properties
            properties = blob_client.get_blob_properties()

            result = StorageFileDownloadServiceReadDto(
                blob_name=data.blob_name,
                content=file_content,
                content_type=properties.content_settings.content_type if properties.content_settings else None,
                size=properties.size
            )

            return Respons[StorageFileDownloadServiceReadDto](
                detail=f"File '{data.blob_name}' downloaded successfully",
                error=None,
                data=[result],
                status_code=200,
                success=True,
            )

        except ResourceNotFoundError:
            return Respons[StorageFileDownloadServiceReadDto](
                detail=f"File '{data.blob_name}' not found",
                error="Resource not found",
                data=[],
                status_code=404,
                success=False,
            )
        except Exception as e:
            return Respons[StorageFileDownloadServiceReadDto](
                detail="Failed to download file",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )

    @staticmethod
    def get_file_url(data: StorageFileUrlServiceWriteDto) -> Respons[StorageFileUrlServiceReadDto]:
        """
        Generate a presigned URL (SAS token) for a file in Azure Storage blob container.
        Note: This requires the storage account to have a shared key available.

        Args:
            data: URL generation parameters including storage account URL, container name,
                  blob name, and expiry time in hours

        Returns:
            Response object containing presigned URL or error information
        """
        try:
            blob_service_client = StorageService._get_blob_service_client(
                data.storage_account_url,
                data.managed_identity_client_id
            )
            blob_client = blob_service_client.get_blob_client(
                container=data.container_name,
                blob=data.blob_name
            )

            # Check if blob exists
            if not blob_client.exists():
                return Respons[StorageFileUrlServiceReadDto](
                    detail=f"File '{data.blob_name}' not found",
                    error="Resource not found",
                    data=[],
                    status_code=404,
                    success=False,
                )

            # Generate user delegation key for SAS token (works with Managed Identity)
            # This requires the managed identity to have "Storage Blob Delegator" role
            delegation_key = blob_service_client.get_user_delegation_key(
                key_start_time=datetime.utcnow(),
                key_expiry_time=datetime.utcnow() + timedelta(hours=data.expiry_hours or 1)
            )

            # Generate SAS token using user delegation key
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=data.container_name,
                blob_name=data.blob_name,
                user_delegation_key=delegation_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=data.expiry_hours or 1)
            )

            # Construct the full URL with SAS token
            presigned_url = f"{blob_client.url}?{sas_token}"

            result = StorageFileUrlServiceReadDto(
                blob_name=data.blob_name,
                presigned_url=presigned_url,
                expires_in_hours=data.expiry_hours or 1
            )

            return Respons[StorageFileUrlServiceReadDto](
                detail=f"Presigned URL generated for '{data.blob_name}'",
                error=None,
                data=[result],
                status_code=200,
                success=True,
            )

        except Exception as e:
            return Respons[StorageFileUrlServiceReadDto](
                detail="Failed to generate presigned URL",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )
