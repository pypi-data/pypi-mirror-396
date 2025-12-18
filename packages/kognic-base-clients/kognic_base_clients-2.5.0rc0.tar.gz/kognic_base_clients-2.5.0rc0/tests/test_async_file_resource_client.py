import pytest
from pytest_httpx import HTTPXMock

from kognic.base_clients.cloud_storage import UploadSpec
from kognic.base_clients.cloud_storage.async_file_resource_client import AsyncFileResourceClient

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
class TestAsyncFileResourceClient:
    async def test_upload_files_local_200(self, httpx_mock: HTTPXMock, put_spec, put_spec_2):
        upload_specs = {
            "random-data.txt": UploadSpec(
                destination=put_spec.url,
                filename=str(put_spec.path),
                content_type="application/octet-stream",
            ),
            "random-data-2.txt": UploadSpec(
                destination=put_spec_2.url,
                filename=str(put_spec_2.path),
                content_type="application/octet-stream",
            ),
        }

        httpx_mock.add_response(url=put_spec.url, method="PUT", status_code=200, match_content=put_spec.content)
        httpx_mock.add_response(url=put_spec_2.url, method="PUT", status_code=200, match_content=put_spec_2.content)
        resource_client = AsyncFileResourceClient(max_retry_attempts=3, max_retry_wait_time=0.1)

        await resource_client.upload_files(upload_specs=upload_specs)
        assert len(httpx_mock.get_requests()) == 2

    async def test_upload_json_500_then_200(self, httpx_mock: HTTPXMock, put_spec):
        httpx_mock.add_response(url=put_spec.url, method="PUT", status_code=500, match_content=put_spec.content)
        httpx_mock.add_response(url=put_spec.url, method="PUT", status_code=500, match_content=put_spec.content)
        httpx_mock.add_response(url=put_spec.url, method="PUT", status_code=200, match_content=put_spec.content)

        resource_client = AsyncFileResourceClient(max_retry_attempts=3, max_retry_wait_time=0.1)
        with open(put_spec.path, "rb") as f:
            await resource_client.upload_json(f, put_spec.url)
        assert len(httpx_mock.get_requests()) == 3

    async def test_download_json_500_then_200(self, httpx_mock: HTTPXMock, get_spec):
        httpx_mock.add_response(url=get_spec.url, method="GET", status_code=500)
        httpx_mock.add_response(url=get_spec.url, method="GET", status_code=500)
        httpx_mock.add_response(url=get_spec.url, method="GET", status_code=200, content=get_spec.result_bytes)

        resource_client = AsyncFileResourceClient(max_retry_attempts=3, max_retry_wait_time=0.1)
        json_response = await resource_client.get_json(get_spec.url)
        assert json_response == get_spec.result_json
        assert len(httpx_mock.get_requests()) == 3
