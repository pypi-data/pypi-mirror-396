"""Client for communicating with the Kognic platform."""

import logging
import urllib.parse
from typing import Optional, Union

from kognic.auth.requests.auth_session import RequestsAuthSession
from pydantic.alias_generators import to_snake
from requests import HTTPError

from kognic.base_clients import __version__
from kognic.base_clients.models import PaginatedResponse
from kognic.base_clients.retry_support import request_with_retry
from kognic.base_clients.util import filter_none

log = logging.getLogger(__name__)

ENVELOPED_JSON_TAG = "data"


class HttpClient:
    """Http Client dealing with auth and communication with API."""

    def __init__(
        self,
        host: str,
        auth=None,
        auth_host: Optional[str] = None,
        client_organization_id: Optional[int] = None,
        timeout: int = 60,
        max_retries: int = 10,
        session: RequestsAuthSession = None,
    ):
        """
        :param host: override for api url
        :param auth: auth credentials, see https://docs.kognic.com/api-guide/advanced-setup#WQ641
        :param auth_host: override for authentication url
        :param client_organization_id: Overrides your users organization id. Only works with a Kognic user.
        :param max_retries: Max number of attempts to retry uploading a file to GCS.
        :param timeout: Max time to wait for response from server.
        :param session: an existing RequestsAuthSession to override auth + auth_host
        """

        self.host = host
        if session:
            self._auth_req_session = session
        else:
            self._auth_req_session = RequestsAuthSession(host=auth_host, auth=auth)

        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": f"kognic-{to_snake(self.__class__.__name__)}/{__version__}",
        }
        self.dryrun_header = {"X-Dryrun": ""}
        self.timeout = timeout
        self.max_retries = max_retries

        if client_organization_id is not None:
            self.headers["X-Organization-Id"] = str(client_organization_id)
            log.warning(
                f"WARNING: You will now act as if you are part of organization: {client_organization_id}. "
                f"This will not work unless you are a Kognic user."
            )

    @property
    def session(self):
        return self._auth_req_session.session

    @staticmethod
    def _http_error_handler(exception: HTTPError) -> None:
        """
        Raises a RuntimeError using error details from an enveloped HTTP 400 response.
        """
        if exception.response is not None and exception.response.status_code == 400:
            try:
                message = exception.response.json()["message"]
            except ValueError:
                message = exception.response.text
            raise RuntimeError(message) from exception
        raise exception from None

    @staticmethod
    def _unwrap_enveloped_json(js: dict) -> Union[dict, list, PaginatedResponse]:
        if isinstance(js, list):
            return js
        elif js is not None and js.get("metadata") is not None:
            return PaginatedResponse.from_json(js)
        elif js is not None and js.get(ENVELOPED_JSON_TAG) is not None:
            return js[ENVELOPED_JSON_TAG]
        return js

    def get(self, endpoint, **kwargs) -> dict:
        r"""Sends a GET request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param \**kwargs: Optional arguments that ``request`` takes.
        :rtype: dict
        """

        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", self.timeout)
        url = urllib.parse.urljoin(self.host, endpoint)
        resp = request_with_retry(self.session.get, self.max_retries, self.timeout, HttpClient._http_error_handler, url=url, **kwargs)
        return self._unwrap_enveloped_json(resp.json())

    def post(self, endpoint, data=None, json=None, dryrun=False, discard_response=False, **kwargs) -> Optional[dict]:
        r"""Sends a POST request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) JSON blob to send
        :param dryrun: (optional) Send a dry-run header with the request.
        :param discard_response: (optional) Ignore the response and return None
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \**kwargs: Optional arguments that ``request`` takes.
        :rtype: dict
        """

        if dryrun:
            headers = {**self.headers, **self.dryrun_header}
        else:
            headers = {**self.headers}

        kwargs.setdefault("headers", headers)
        kwargs.setdefault("timeout", self.timeout)
        resp = request_with_retry(
            self.session.post,
            self.max_retries,
            self.timeout,
            HttpClient._http_error_handler,
            url=f"{self.host}/{endpoint}",
            data=data,
            json=filter_none(json),
            **kwargs,
        )
        if discard_response:
            return None
        else:
            return self._unwrap_enveloped_json(resp.json())

    def put(self, endpoint, data, **kwargs) -> dict:
        r"""Sends a PUT request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \**kwargs: Optional arguments that ``request`` takes.
        :rtype: dict
        """
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", self.timeout)
        resp = request_with_retry(
            self.session.put,
            self.max_retries,
            self.timeout,
            HttpClient._http_error_handler,
            url=f"{self.host}/{endpoint}",
            data=filter_none(data),
            **kwargs,
        )
        return self._unwrap_enveloped_json(resp.json())

    def patch(self, endpoint, data=None, discard_response=False, **kwargs) -> dict:
        r"""Sends a PATCH request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \**kwargs: Optional arguments that ``request`` takes.
        :rtype: dict
        """
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", self.timeout)
        resp = request_with_retry(
            self.session.patch,
            self.max_retries,
            self.timeout,
            HttpClient._http_error_handler,
            url=f"{self.host}/{endpoint}",
            data=filter_none(data),
            **kwargs,
        )
        return None if discard_response else self._unwrap_enveloped_json(resp.json())

    def delete(self, endpoint, dryrun=False, discard_response=False, **kwargs) -> Optional[dict]:
        r"""Sends a DELETE request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param dryrun: (optional) Send a dry-run header with the request.
        :param discard_response: (optional) Ignore the response and return None
        :param \**kwargs: Optional arguments that ``request`` takes.
        :rtype: Optional[dict]
        """

        headers = {**self.headers, **self.dryrun_header} if dryrun else {**self.headers}

        kwargs.setdefault("headers", headers)
        kwargs.setdefault("timeout", self.timeout)
        url = urllib.parse.urljoin(self.host, endpoint)
        resp = request_with_retry(self.session.delete, self.max_retries, self.timeout, HttpClient._http_error_handler, url=url, **kwargs)

        return None if discard_response else self._unwrap_enveloped_json(resp.json())
