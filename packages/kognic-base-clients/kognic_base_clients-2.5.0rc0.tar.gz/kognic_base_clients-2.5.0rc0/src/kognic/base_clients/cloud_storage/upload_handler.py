import asyncio
import logging
from typing import Any, AsyncGenerator, BinaryIO, Callable, Dict, Mapping, Optional

import httpx

from kognic.base_clients.async_retry_support import request_with_retry
from kognic.base_clients.cloud_storage.network_limits import DEFAULT_MAX_NR_CONNECTIONS, get_network_limits, get_network_timeouts
from kognic.base_clients.cloud_storage.upload_spec import UploadableData, UploadSpec

log = logging.getLogger(__name__)


class UploadHandler:
    def __init__(
        self,
        max_retry_attempts: int = 23,
        max_retry_wait_time: float = 60.0,
        timeout: int = 60,
        max_connections: int = DEFAULT_MAX_NR_CONNECTIONS,
    ) -> None:
        """
        :param max_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_retry_wait_time:  Max with time before retrying an upload to GCS.
        :param timeout: Max time to wait for response from server.
        :param max_connections: Max nr network connections to apply to the http client.
        """
        self.max_num_retries = max_retry_attempts
        self.max_retry_wait_time = max_retry_wait_time  # seconds
        self.timeout = timeout  # seconds
        self.httpx_limits = get_network_limits(max_connections)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(limits=self.httpx_limits, timeout=get_network_timeouts(self.timeout))

    async def _upload_file(self, httpx_client: httpx.AsyncClient, upload_url: str, file: UploadableData, headers: Dict[str, str]) -> None:
        """
        Upload the file to GCS, retries if the upload fails with some specific status codes or timeouts.
        """
        await request_with_retry(
            httpx_client.put,
            self.max_num_retries,
            self.max_retry_wait_time,
            url=upload_url,
            content=file.read() if hasattr(file, "read") else file,
            headers=headers,
        )

    async def _upload_stream(
        self,
        httpx_client: httpx.AsyncClient,
        upload_url: str,
        get_stream: Callable[..., AsyncGenerator[bytes, Any]],
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Upload the file to GCS, retries if the upload fails with some specific status codes or timeouts.
        """
        headers = headers or {}

        def method():
            return httpx_client.put(
                content=get_stream(),
                url=upload_url,
                headers=headers,
            )

        await request_with_retry(
            method,
            self.max_num_retries,
            self.max_retry_wait_time,
        )

    async def upload_files(self, upload_specs: Mapping[str, UploadSpec]) -> None:
        """
        Upload all files to cloud storage

        :param upload_specs: map between filename and details of what to upload where
        """

        async def create_task(client: httpx.AsyncClient, upload_spec: UploadSpec):
            if upload_spec.data is None and upload_spec.callback is None:
                await self._upload_from_local_file(client, upload_spec)
            elif upload_spec.data is not None:
                await self._upload_from_blob(client, upload_spec)
            elif upload_spec.callback is not None:
                await self._upload_from_callback(client, upload_spec)

        async with self._client() as httpx_client:
            tasks = [asyncio.create_task(create_task(httpx_client, upload_spec)) for upload_spec in upload_specs.values()]
            await asyncio.gather(*tasks)

    async def upload_file_as_stream(self, httpx_client: httpx.AsyncClient, upload_spec: UploadSpec) -> None:
        async with self._client() as httpx_client:
            await self._upload_from_local_file(httpx_client, upload_spec)

    async def upload_file(self, file: BinaryIO, url: str) -> None:
        headers = {"Content-Type": "application/json"}
        async with self._client() as httpx_client:
            await self._upload_file(httpx_client, url, file, headers)

    async def _upload(self, httpx_client: httpx.AsyncClient, upload_spec: UploadSpec, data: UploadableData):
        headers = {"Content-Type": upload_spec.content_type}
        await self._upload_file(httpx_client, upload_spec.destination, data, headers)

    async def _upload_from_blob(self, httpx_client: httpx.AsyncClient, upload_spec: UploadSpec):
        log.debug(f"Blob upload for filename={upload_spec.filename}")
        await self._upload(httpx_client, upload_spec, upload_spec.data)

    async def _upload_from_local_file(self, httpx_client: httpx.AsyncClient, upload_spec: UploadSpec):
        log.debug(f"Upload from local file for filename={upload_spec.filename}")
        headers = {"Content-Type": upload_spec.content_type}

        def get_stream() -> AsyncGenerator[bytes, Any]:
            return self._file_stream(upload_spec.filename)

        await self._upload_stream(httpx_client, upload_spec.destination, get_stream, headers)

    async def _upload_from_callback(self, httpx_client: httpx.AsyncClient, upload_spec: UploadSpec):
        log.debug(f"Upload from callback for filename={upload_spec.filename}")
        try:
            if asyncio.iscoroutinefunction(upload_spec.callback):
                data = await upload_spec.callback(upload_spec.filename)
            else:
                # async generators go here too, which seems to be what httpx expects.
                data = upload_spec.callback(upload_spec.filename)
            await self._upload(httpx_client, upload_spec, data)
        except Exception as e:
            raise RuntimeError("Failed to upload file: callback failed", e)

    @staticmethod
    async def _file_stream(filename: str) -> AsyncGenerator[bytes, Any]:
        with open(filename, "rb") as f:
            while chunk := f.read(64 * 1024):
                yield chunk
