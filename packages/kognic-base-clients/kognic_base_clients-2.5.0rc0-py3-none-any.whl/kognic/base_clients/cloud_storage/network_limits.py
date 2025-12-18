import httpx

DEFAULT_MAX_NR_CONNECTIONS = 10
NETWORK_CONNECTIONS_FACTOR = 5


def get_network_limits(max_nr_connections: int = DEFAULT_MAX_NR_CONNECTIONS) -> httpx.Limits:
    max_keepalive_connections = int(max_nr_connections / NETWORK_CONNECTIONS_FACTOR)
    if max_keepalive_connections <= 0:
        max_keepalive_connections = 1
    return httpx.Limits(max_keepalive_connections=max_keepalive_connections, max_connections=max_nr_connections)


def get_network_timeouts(timeout: int = 60) -> httpx.Timeout:
    return httpx.Timeout(timeout, pool=None, write=3600)
