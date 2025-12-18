import httpx
import pytest
from pytest_httpx import HTTPXMock

from kognic.base_clients.cloud_storage.download_handler import DownloadHandler

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
class TestAsyncDownloadHandler:
    async def test_download_json_200(self, httpx_mock: HTTPXMock, get_spec):
        httpx_mock.add_response(method="GET", status_code=200, url=get_spec.url, content=get_spec.result_bytes)
        async_download_handler = DownloadHandler()
        json_response = await async_download_handler.get_json(get_spec.url)
        assert json_response == get_spec.result_json
        assert len(httpx_mock.get_requests()) == 1

    async def test_download_json_400(self, httpx_mock: HTTPXMock, get_spec):
        httpx_mock.add_response(method="GET", status_code=400, url=get_spec.url)
        async_download_handler = DownloadHandler()
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_download_handler.get_json(get_spec.url)
        assert exc_info.value.response.status_code == 400
        assert len(httpx_mock.get_requests()) == 1

    async def test_download_json_500(self, httpx_mock: HTTPXMock, get_spec):
        httpx_mock.add_response(method="GET", status_code=500, url=get_spec.url, is_reusable=True)
        async_download_handler = DownloadHandler(max_retry_attempts=3, max_retry_wait_time=0.1)
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_download_handler.get_json(get_spec.url)
        assert exc_info.value.response.status_code == 500
        assert len(httpx_mock.get_requests()) == 4

    async def test_download_json_500_then_200(self, httpx_mock: HTTPXMock, get_spec):
        httpx_mock.add_response(method="GET", status_code=500, url=get_spec.url)
        httpx_mock.add_response(method="GET", status_code=500, url=get_spec.url)
        httpx_mock.add_response(method="GET", status_code=200, url=get_spec.url, content=get_spec.result_bytes)
        async_download_handler = DownloadHandler(max_retry_attempts=3, max_retry_wait_time=0.1)
        json_response = await async_download_handler.get_json(get_spec.url)
        assert json_response == get_spec.result_json
        assert len(httpx_mock.get_requests()) == 3
