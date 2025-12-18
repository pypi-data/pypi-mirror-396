import tempfile
from pathlib import Path

import aiofiles
import pytest
from conftest import PutSpec
from pytest_httpx import HTTPXMock

from kognic.base_clients.cloud_storage import UploadSpec
from kognic.base_clients.cloud_storage.upload_handler import UploadHandler

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
class TestAsyncUploadHandler:
    async def test_large_file_500_then_200(self, httpx_mock: HTTPXMock):
        file = tempfile.NamedTemporaryFile(delete=False)
        # The _file_stream method in UploadHandler reads files in 64 KB chunks,
        # so we create a file larger than that to test chunked uploading.
        file.write(b"a" * 64 * 1024 + b"b" * 64 * 1024)  # 128 KB file
        file.close()
        url = "https://storage.googleapis.com/upload/storage/v1/b/my-bucket/o?uploadType=media&name=large-file.txt"
        httpx_mock.add_response(method="PUT", status_code=500, url=url, match_content=b"a" * 64 * 1024 + b"b" * 64 * 1024)
        httpx_mock.add_response(method="PUT", status_code=200, url=url, match_content=b"a" * 64 * 1024 + b"b" * 64 * 1024)
        async_upload_handler = UploadHandler(max_retry_attempts=3, max_retry_wait_time=0.1)
        await async_upload_handler.upload_files(
            {file.name: UploadSpec(destination=url, filename=file.name, content_type="application/octet-stream")}
        )

    async def test_upload_file_200(self, httpx_mock: HTTPXMock, put_spec: PutSpec):
        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec.url, match_content=put_spec.content)
        async_upload_handler = UploadHandler(max_retry_attempts=3, max_retry_wait_time=0.1)
        with open(put_spec.path, "rb") as f:
            await async_upload_handler.upload_file(f, put_spec.url)
        assert len(httpx_mock.get_requests()) == 1

    async def test_upload_file_500_then_200(self, httpx_mock: HTTPXMock, put_spec: PutSpec):
        httpx_mock.add_response(method="PUT", status_code=500, url=put_spec.url, match_content=put_spec.content)
        httpx_mock.add_response(method="PUT", status_code=500, url=put_spec.url, match_content=put_spec.content)
        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec.url, match_content=put_spec.content)
        async_upload_handler = UploadHandler(max_retry_attempts=3, max_retry_wait_time=0.1)
        with open(put_spec.path, "rb") as f:
            await async_upload_handler.upload_file(f, put_spec.url)
        assert len(httpx_mock.get_requests()) == 3

    async def test_upload_files_local_200(self, httpx_mock: HTTPXMock, put_spec: PutSpec, put_spec_2: PutSpec):
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

        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec.url, match_content=put_spec.content)
        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec_2.url, match_content=put_spec_2.content)
        async_upload_handler = UploadHandler()

        await async_upload_handler.upload_files(upload_specs=upload_specs)
        assert len(httpx_mock.get_requests()) == 2

    async def test_upload_files_file_data_200(self, httpx_mock: HTTPXMock, put_spec: PutSpec, put_spec_2: PutSpec):
        file_content = put_spec.content
        file_content_2 = put_spec_2.content
        upload_specs = {
            "random-data.txt": UploadSpec(
                destination=put_spec.url,
                filename=str(put_spec.path),
                content_type="application/octet-stream",
                data=file_content,
            ),
            "random-data-2.txt": UploadSpec(
                destination=put_spec_2.url,
                filename=str(put_spec_2.path),
                content_type="application/octet-stream",
                data=file_content_2,
            ),
        }

        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec.url, match_content=file_content)
        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec_2.url, match_content=file_content_2)

        async_upload_handler = UploadHandler()

        await async_upload_handler.upload_files(upload_specs=upload_specs)
        assert len(httpx_mock.get_requests()) == 2

    async def test_upload_files_callback_200(self, httpx_mock: HTTPXMock, put_spec: PutSpec, put_spec_2: PutSpec):
        upload_specs = {
            "random-data.txt": UploadSpec(
                destination=put_spec.url,
                filename=str(put_spec.path),
                content_type="application/octet-stream",
                callback=lambda fname: Path(fname).open("rb"),
            ),
            "random-data-2.txt": UploadSpec(
                destination=put_spec_2.url,
                filename=str(put_spec_2.path),
                content_type="application/octet-stream",
                callback=lambda fname: Path(fname).open("rb").read(),
            ),
        }

        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec.url, match_content=put_spec.content)
        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec_2.url, match_content=put_spec_2.content)

        async_upload_handler = UploadHandler()

        await async_upload_handler.upload_files(upload_specs=upload_specs)
        assert len(httpx_mock.get_requests()) == 2

    async def test_upload_files_async_callback_200(self, httpx_mock: HTTPXMock, put_spec: PutSpec, put_spec_2: PutSpec):
        async def callback(fname: str) -> bytes:
            async with aiofiles.open(fname, "rb") as f:
                return await f.read()

        upload_specs = {
            "random-data.txt": UploadSpec(
                destination=put_spec.url,
                filename=str(put_spec.path),
                content_type="application/octet-stream",
                callback=callback,
            ),
            "random-data-2.txt": UploadSpec(
                destination=put_spec_2.url,
                filename=str(put_spec_2.path),
                content_type="application/octet-stream",
                callback=callback,
            ),
        }

        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec.url, match_content=put_spec.content)
        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec_2.url, match_content=put_spec_2.content)

        async_upload_handler = UploadHandler()

        await async_upload_handler.upload_files(upload_specs=upload_specs)
        assert len(httpx_mock.get_requests()) == 2

    async def test_upload_files_when_async_callback_failed(self, httpx_mock: HTTPXMock, put_spec: PutSpec, put_spec_2: PutSpec):
        async def callback(fname: str) -> bytes:
            async with aiofiles.open("I-don't-exist.txt", "rb") as f:
                return await f.read()

        upload_specs = {
            "random-data.txt": UploadSpec(
                destination=put_spec.url,
                filename=str(put_spec.path),
                content_type="application/octet-stream",
                callback=lambda fname: Path(fname).open("rb"),
            ),
            "random-data-2.txt": UploadSpec(
                destination=put_spec_2.url,
                filename=str(put_spec_2.path),
                content_type="application/octet-stream",
                callback=callback,
            ),
        }

        httpx_mock.add_response(method="PUT", status_code=200, url=put_spec.url, match_content=put_spec.content)

        async_upload_handler = UploadHandler()

        with pytest.raises(RuntimeError) as exc_info:
            await async_upload_handler.upload_files(upload_specs=upload_specs)
            assert exc_info.value.args[0] == "Failed to upload file: callback failed"
            assert isinstance(exc_info.value.args[1], FileNotFoundError)

        assert len(httpx_mock.get_requests()) == 1
