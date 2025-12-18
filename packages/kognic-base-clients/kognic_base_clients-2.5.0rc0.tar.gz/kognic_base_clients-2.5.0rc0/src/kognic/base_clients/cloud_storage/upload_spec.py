from io import IOBase
from typing import Any, AsyncGenerator, Awaitable, BinaryIO, Callable, Generator, Optional, Union

UploadableData = Union[bytes, BinaryIO, IOBase, Generator[bytes, Any, None], AsyncGenerator[bytes, Any]]
SyncCallback = Callable[[str], UploadableData]
AsyncCallback = Callable[[str], Awaitable[UploadableData]]
Callback = Union[SyncCallback, AsyncCallback]


class UploadSpec:
    """
    Represents an upload to be performed to some resource ID: what is to be uploaded and where.
    A filename must always be set, and a data blob or callback may optionally be set. With just a filename this upload
    will use the named file. With a filename and a blob, the data blob is used and the filename is informational only.
    If a callback is set, it will be called with the filename as its argument and must return a blob (bytes) for upload.
    """

    destination: str
    filename: str
    content_type: str
    data: Optional[UploadableData]
    callback: Optional[Callback]

    def __init__(
        self,
        destination: str,
        content_type: str,
        filename: Optional[str] = None,
        data: Optional[UploadableData] = None,
        callback: Optional[Callback] = None,
    ):
        self.destination = destination
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.callback = callback

    def __repr__(self):
        data_part = "" if self.data is None else f", data ({type(self.data).__name__})"
        cb_part = "" if self.callback is None else ", callback"
        return f"UploadSpec({self.content_type}, destination={self.destination}, filename={self.filename}{data_part}{cb_part})"
