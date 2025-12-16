from pydantic import BaseModel
from .storage_base import (
    StorageConnectionBase,
    StorageFileUploadBase,
    StorageFileUpdateBase,
    StorageFileDeleteBase,
    StorageFileDownloadBase,
    StorageFileUrlBase,
    StorageContainerCreateBase
)


# Container Creation

class StorageContainerCreateControllerWriteDto(StorageContainerCreateBase):
    pass


class StorageContainerCreateServiceWriteDto(StorageContainerCreateControllerWriteDto):
    pass


# File Upload

class StorageFileUploadControllerWriteDto(StorageFileUploadBase):
    pass


class StorageFileUploadServiceWriteDto(StorageFileUploadControllerWriteDto):
    pass


# File Update

class StorageFileUpdateControllerWriteDto(StorageFileUpdateBase):
    pass


class StorageFileUpdateServiceWriteDto(StorageFileUpdateControllerWriteDto):
    pass


# File Delete

class StorageFileDeleteControllerWriteDto(StorageFileDeleteBase):
    pass


class StorageFileDeleteServiceWriteDto(StorageFileDeleteControllerWriteDto):
    pass


# File Download

class StorageFileDownloadControllerWriteDto(StorageFileDownloadBase):
    pass


class StorageFileDownloadServiceWriteDto(StorageFileDownloadControllerWriteDto):
    pass


# File URL

class StorageFileUrlControllerWriteDto(StorageFileUrlBase):
    pass


class StorageFileUrlServiceWriteDto(StorageFileUrlControllerWriteDto):
    pass
