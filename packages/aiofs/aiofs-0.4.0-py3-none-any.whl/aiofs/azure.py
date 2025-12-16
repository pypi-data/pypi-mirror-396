"""Implementation of FileLike with azure blobs"""

import fnmatch
from dataclasses import dataclass
from typing import Self

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobClient, BlobServiceClient

from . import FileLike, FileLikeSystem


@dataclass
class AzureContainerConfig:
    account_name: str
    account_key: str
    container_name: str
    protocol: str = "https"
    endpoint_suffix: str = "core.windows.net"

    @property
    def connection_string(self) -> str:
        """Dynamically generates the Azure Storage Connection String"""
        return (
            f"DefaultEndpointsProtocol={self.protocol};"
            f"AccountName={self.account_name};"
            f"AccountKey={self.account_key};"
            f"EndpointSuffix={self.endpoint_suffix}"
        )


class AzFileLike(FileLike):
    """Implementation of FileLike in azure blobs"""

    def __init__(self, blob: BlobClient, mode: str = "r"):
        self._blob = blob
        self._lease = None
        self._content = b""
        self._mode = mode
        self._lease = None
        self._context = None

    async def __aenter__(self) -> Self:
        self._context = self._blob = await self._blob.__aenter__()
        if "w" in self._mode or "r+" in self._mode:
            try:
                self._lease = await self._blob.acquire_lease(15)
            except ResourceNotFoundError:
                ...
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._blob.__aexit__(exc_type, exc, tb)

        try:
            if self._content:
                await self._blob.upload_blob(
                    self._content, overwrite=True, lease=self._lease
                )
        except ResourceExistsError:
            raise BlockingIOError(f"")
        finally:
            if self._lease:
                await self._lease.release()

    async def read(self, size: int = -1) -> bytes:
        if not self._context:
            raise RuntimeError('Call to "read" out of context')
        if size >= 0:
            raise NotImplementedError("Not designed to donwload partially")

        try:
            stream = await self._blob.download_blob()
        except ResourceNotFoundError:
            raise FileNotFoundError(f"Not found {self._blob.blob_name}")
        return await stream.readall()

    async def write(self, b: bytes):
        if not self._context:
            raise RuntimeError('Call to "write" out of context')
        self._content += b


class AzFileSystem(FileLikeSystem):
    """Create and manage AzFileLike"""

    def __init__(
        self,
        config: AzureContainerConfig,
        file_pattern: str = "*",
    ):
        print(config.connection_string)
        self._assert_container_exists(config)
        self._service = BlobServiceClient.from_connection_string(
            config.connection_string
        )
        self._container = self._service.get_container_client(config.container_name)

        self._pattern = file_pattern

    def open(self, filename: str, mode="r") -> AzFileLike:
        blob_name = self._pattern.replace("*", filename)
        blob = self._container.get_blob_client(blob_name)

        return AzFileLike(blob, mode)

    async def rm(self, pattern: str):
        filenames = await self.ls(pattern)
        for fn in filenames:
            blob_name = self._pattern.replace("*", fn)
            blob = self._container.get_blob_client(blob_name)
            try:
                await blob.delete_blob()
            except ResourceNotFoundError:
                pass

    async def close(self):
        if self._container:
            await self._container.close()
        await self._service.close()

    async def ls(self, pattern: str = "*"):
        """List all filenames of the system"""
        prefix, _, sufix = self._pattern.partition("*")
        names = []
        prefix = prefix if prefix else None
        pre = 0 if prefix is None else len(prefix)
        suf = -len(sufix) if sufix else None
        async for blob in self._container.list_blobs(prefix):
            if blob.name.endswith(sufix):
                names.append(blob.name[pre:suf])
        return fnmatch.filter(names, pattern)

    def _assert_container_exists(self, cfg: AzureContainerConfig):
        with SyncBlobServiceClient.from_connection_string(
            cfg.connection_string
        ) as service:
            if not service.get_container_client(cfg.container_name).exists():
                service.create_container(cfg.container_name)
