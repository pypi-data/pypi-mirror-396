import random
from typing import Mapping

from urllib3.util import Url, parse_url

RETRYABLE_STATUS_CODES = [408, 429, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 598, 599]
GCS_SCHEME = "gs"


def filter_none(js: dict) -> dict:
    if isinstance(js, Mapping):
        return {k: filter_none(v) for k, v in js.items() if v is not None}
    else:
        return js


def get_resource_id(signed_url: str) -> str:
    url = parse_url(signed_url)
    resource_id = Url(scheme=GCS_SCHEME, path=url.path)
    return str(resource_id).replace("///", "//")


# https://cloud.google.com/iot/docs/how-tos/exponential-backoff
def get_wait_time(upload_attempt: int, max_retry_wait_time: float) -> float:
    """
    Calculates the wait time before attempting another file upload or download

    :param upload_attempt: How many attempts to upload that have been made
    :param max_retry_wait_time: How long to wait (max) between retries
    :return: int: The time to wait before retrying upload
    """
    initial_wait_time_seconds: int = pow(2, upload_attempt - 1)
    wait_time_seconds: float = initial_wait_time_seconds + random.random()
    wait_time_seconds: float = wait_time_seconds if wait_time_seconds < max_retry_wait_time else max_retry_wait_time
    return wait_time_seconds
