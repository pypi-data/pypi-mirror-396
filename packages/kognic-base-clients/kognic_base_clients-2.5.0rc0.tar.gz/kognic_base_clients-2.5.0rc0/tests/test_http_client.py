import time
from uuid import uuid4

import pytest
import responses
from authlib.oauth2.auth import OAuth2Token
from requests.exceptions import HTTPError

from kognic.base_clients.http_client import HttpClient

base_url = "https://api.mocked.com"
auth_host = "https://api.auth.mocked.com"

http_client = HttpClient(auth=(1, 2), host=base_url, auth_host=auth_host)


def test_http_client_creation_with_auth_None():
    HttpClient(auth=None, host=base_url, auth_host=auth_host)


def mock_auth():
    responses.add(
        responses.POST,
        f"{auth_host}/v1/auth/oauth/token",
        status=200,
        json=OAuth2Token(
            {
                "access_token": "the-token",
                "expires_in": 200,
                "expires_at": time.time() + 200,
            }
        ),
    )


@responses.activate
def test_delete():
    mock_auth()

    resource_uuid = uuid4()
    responses.add(
        responses.DELETE,
        f"{base_url}/v1/resources/{resource_uuid}",
        status=200,
        json={"message": "success"},
    )
    response = http_client.delete(f"{base_url}/v1/resources/{resource_uuid}")
    assert response == {"message": "success"}


@responses.activate
def test_delete_discard():
    mock_auth()

    resource_uuid = uuid4()
    responses.add(
        responses.DELETE,
        f"{base_url}/v1/resources/{resource_uuid}",
        status=200,
        json={"message": "success"},
    )
    response = http_client.delete(f"{base_url}/v1/resources/{resource_uuid}", discard_response=True)
    assert response is None


@responses.activate
def test_delete_on_not_found():
    mock_auth()

    resource_uuid = uuid4()
    responses.add(
        responses.DELETE,
        f"{base_url}/v1/resources/{resource_uuid}",
        status=404,
        json={"message": "not found"},
    )
    with pytest.raises(HTTPError) as e:
        http_client.delete(f"{base_url}/v1/resources/{resource_uuid}")
    assert str(e.value).startswith("404 Client Error: Not Found for url")


@responses.activate
def test_delete_with_dryrun():
    mock_auth()

    resource_uuid = uuid4()
    responses.add(
        responses.DELETE,
        f"{base_url}/v1/resources/{resource_uuid}",
        status=200,
        json={"message": "success"},
        match=[responses.matchers.header_matcher({"X-Dryrun": ""})],
    )
    response = http_client.delete(f"{base_url}/v1/resources/{resource_uuid}", dryrun=True)
    assert response == {"message": "success"}
