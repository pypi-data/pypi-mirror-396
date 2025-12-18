"""Client for communicating with the Kognic platform."""

import logging
from typing import BinaryIO, Dict, Mapping

from kognic.base_clients.cloud_storage.download_handler import DownloadHandler
from kognic.base_clients.cloud_storage.upload_handler import UploadHandler
from kognic.base_clients.cloud_storage.upload_spec import UploadSpec

log = logging.getLogger(__name__)


class AsyncFileResourceClient:
    def __init__(
        self,
        max_retry_attempts: int = 23,
        max_retry_wait_time: float = 60.0,
        timeout: int = 60,
        max_connections: int = 10,
    ) -> None:
        """
        :param max_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_retry_wait_time:  Max with time before retrying an upload to GCS.
        :param timeout: Max time to wait for response from server.
        :param max_connections: Max nr network connections to apply to the http client.
        """
        self._upload_handler = UploadHandler(max_retry_attempts, max_retry_wait_time, timeout, max_connections)
        self._download_handler = DownloadHandler(max_retry_attempts, max_retry_wait_time, timeout, max_connections)

    async def upload_files(self, upload_specs: Mapping[str, UploadSpec]) -> None:
        """
        Upload all files to cloud storage

        :param upload_specs: Mapping from a source name to a destination and source of content for an upload
        """
        await self._upload_handler.upload_files(upload_specs=upload_specs)

    async def upload_json(self, file: BinaryIO, url: str) -> None:
        """
        Upload a single file to storage, using the specified url
        :param file: A binary representation of the file
        :param url: The url ot upload to file to
        """

        await self._upload_handler.upload_file(file, url)

    async def get_json(self, url: str) -> Dict:
        """
        Downloads a json from cloud storage

        :param url: Signed URL to GCS resource to download
        """
        return await self._download_handler.get_json(url)
