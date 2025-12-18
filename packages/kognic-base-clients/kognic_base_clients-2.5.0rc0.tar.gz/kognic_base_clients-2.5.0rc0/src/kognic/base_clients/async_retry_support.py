import asyncio
import logging
from typing import Awaitable, Callable, Optional

import httpx

from kognic.base_clients.util import RETRYABLE_STATUS_CODES, get_wait_time

log = logging.getLogger(__name__)

AsyncHTTPErrorHandler = Callable[[httpx.HTTPStatusError], None]


#  Using similar retry strategy as gsutil
#  https://cloud.google.com/storage/docs/gsutil/addlhelp/RetryHandlingStrategy
async def request_with_retry(
    method: Callable[..., Awaitable[httpx.Response]],
    max_num_retries: int,
    max_retry_wait_time: float,
    http_error_handler: Optional[AsyncHTTPErrorHandler] = None,
    *args,
    **kwargs,
) -> httpx.Response:
    return await _request_with_retry(method, max_num_retries, max_num_retries, max_retry_wait_time, http_error_handler, *args, **kwargs)


async def _request_with_retry(
    method: Callable[..., Awaitable[httpx.Response]],
    number_of_retries: int,
    max_num_retries: int,
    max_retry_wait_time: float,
    http_error_handler: Optional[AsyncHTTPErrorHandler] = None,
    *args,
    **kwargs,
) -> httpx.Response:
    """
    Retrying HTTP request with exponential backoff.

    :param method: HTTP method executor (probably something like requests.put, auth_session.put).
    :param number_of_retries: Remaining number of retries
    :param max_num_retries: Max number of retry attempts
    :param max_retry_wait_time: Upper bound on wait time between retries (seconds)
    :param http_error_handler Optional handler for HTTP errors that are not retryable
    :param args: Named args for `method`
    :param kwargs: kwargs for `method`
    :return: Response
    """

    async def handle_error(error_type: str, re: httpx.HTTPError, retries_remaining: int):
        if retries_remaining > 0:
            await _generic_error(error_type, retries_remaining, max_num_retries, max_retry_wait_time)
            return await _request_with_retry(
                method, retries_remaining - 1, max_num_retries, max_retry_wait_time, http_error_handler, *args, **kwargs
            )
        else:
            log.error("Request error, no more retries left", exc_info=re)
            raise re

    try:
        resp = await method(*args, **kwargs)
        resp.raise_for_status()
        return resp
    except httpx.HTTPStatusError as e:
        if e.response.status_code in RETRYABLE_STATUS_CODES:
            return await handle_error("Retryable HTTP error", e, number_of_retries)
        elif http_error_handler is not None:
            http_error_handler(e)
        else:
            raise e
    except httpx.TimeoutException as e:
        return await handle_error("Network timeout", e, number_of_retries)
    except httpx.TransportError as e:
        return await handle_error("Connection error", e, number_of_retries)


async def _generic_error(error_type: str, number_of_retries: int, max_num_retries: int, max_retry_wait_time: float) -> None:
    upload_attempt = max_num_retries - number_of_retries + 1
    wait_time = get_wait_time(upload_attempt, max_retry_wait_time)
    log.warning(
        f"Failed to send request. {error_type}" f"Attempt {upload_attempt}/{max_num_retries}, retrying in {int(wait_time)} seconds."
    )
    await asyncio.sleep(wait_time)
