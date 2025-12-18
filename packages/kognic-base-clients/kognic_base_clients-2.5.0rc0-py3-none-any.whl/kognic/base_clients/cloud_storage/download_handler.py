import json
import logging
from typing import Dict

import httpx

from kognic.base_clients.async_retry_support import request_with_retry
from kognic.base_clients.cloud_storage.network_limits import DEFAULT_MAX_NR_CONNECTIONS, get_network_limits, get_network_timeouts

log = logging.getLogger(__name__)


class DownloadHandler:
    def __init__(
        self,
        max_retry_attempts: int = 23,
        max_retry_wait_time: float = 60.0,
        timeout: int = 60,
        max_connections: int = DEFAULT_MAX_NR_CONNECTIONS,
    ) -> None:
        """
        :param max_retry_attempts: Max number of attempts to retry requests to GCS.
        :param max_retry_wait_time:  Max with time before retrying requests to GCS.
        :param timeout: Max time to wait for response from server.
        :param max_connections: Max nr connections to apply to the httpx client.
        """
        self.max_num_retries = max_retry_attempts
        self.max_retry_wait_time = max_retry_wait_time  # seconds
        self.timeout = timeout  # seconds
        self.httpx_limits = get_network_limits(max_connections)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(limits=self.httpx_limits, timeout=get_network_timeouts(self.timeout))

    async def get_json(self, url: str) -> Dict:
        return json.loads(await self._download_file(url, self.max_num_retries))

    async def _download_file(self, url: str, number_of_retries: int) -> bytes:
        """
        Download a json file from cloud storage

        :param url: URL of file to download
        :param number_of_retries: Number of download attempts before we stop trying to download
        :return: JSON deserialized to dictionary
        """

        async with self._client() as httpx_client:
            resp = await request_with_retry(
                httpx_client.get,
                number_of_retries,
                self.max_retry_wait_time,
                url=url,
            )

        return resp.content
