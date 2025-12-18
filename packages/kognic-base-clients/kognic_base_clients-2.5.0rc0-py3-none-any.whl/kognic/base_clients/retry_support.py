import logging
import time
from typing import Callable, Optional

from requests import ConnectionError, HTTPError, RequestException, Response, Timeout

from kognic.base_clients.util import RETRYABLE_STATUS_CODES, get_wait_time

log = logging.getLogger(__name__)

HTTPErrorHandler = Callable[[HTTPError], None]


def request_with_retry(
    method: Callable[..., Response],
    max_num_retries: int,
    max_retry_wait_time: int,
    http_error_handler: Optional[HTTPErrorHandler] = None,
    *args,
    **kwargs,
) -> Response:
    return _request_with_retry(method, max_num_retries, max_num_retries, max_retry_wait_time, http_error_handler, *args, **kwargs)


def _request_with_retry(
    method: Callable[..., Response],
    number_of_retries: int,
    max_num_retries: int,
    max_retry_wait_time: int,
    http_error_handler: Optional[HTTPErrorHandler] = None,
    *args,
    **kwargs,
) -> Response:
    """
    Retrying HTTP request with exponential backoff.

    :param method: HTTP method executor (probably something like requests.put, auth_session.put).
    :param number_of_retries: Remaining number of retries
    :param max_num_retries: Max number of retry attempts
    :param max_retry_wait_time: Upper bound on wait time between retries (seconds)
    :param args: Named args for `method`
    :param kwargs: kwargs for `method`
    :return: Response
    """

    def handle_error(error_type: str, re: RequestException, retries_remaining: int):
        if retries_remaining > 0:
            _generic_error(error_type, retries_remaining, max_num_retries, max_retry_wait_time)
            return _request_with_retry(
                method, retries_remaining - 1, max_num_retries, max_retry_wait_time, http_error_handler, *args, **kwargs
            )
        else:
            log.error("Request error, no more retries left", re)
            raise re

    try:
        resp = method(*args, **kwargs)
        resp.raise_for_status()
        return resp
    except HTTPError as e:
        if e.response.status_code in RETRYABLE_STATUS_CODES:
            return handle_error("Retryable HTTP error", e, number_of_retries)
        elif http_error_handler is not None:
            http_error_handler(e)
        else:
            raise e
    except Timeout as e:
        return handle_error("Network timeout", e, number_of_retries)
    except ConnectionError as e:
        return handle_error("Connection error", e, number_of_retries)


def _generic_error(error_type: str, number_of_retries: int, max_num_retries: int, max_retry_wait_time: int) -> None:
    upload_attempt = max_num_retries - number_of_retries + 1
    wait_time = get_wait_time(upload_attempt, max_retry_wait_time)
    log.warning(f"Failed to upload file. {error_type}" f"Attempt {upload_attempt}/{max_num_retries}, retrying in {int(wait_time)} seconds.")
    time.sleep(wait_time)
