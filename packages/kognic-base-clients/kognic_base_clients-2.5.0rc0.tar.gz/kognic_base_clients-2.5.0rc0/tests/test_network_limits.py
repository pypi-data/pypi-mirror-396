from kognic.base_clients.cloud_storage.network_limits import get_network_limits


def test_get_network_limits_with_10():
    limits = get_network_limits(10)
    assert limits.max_keepalive_connections == 2
    assert limits.max_connections == 10


def test_get_network_limits_with_5():
    limits = get_network_limits(5)
    assert limits.max_keepalive_connections == 1
    assert limits.max_connections == 5


def test_get_network_limits_with_100():
    limits = get_network_limits(100)
    assert limits.max_keepalive_connections == 20
    assert limits.max_connections == 100


def test_get_network_limits_with_4():
    limits = get_network_limits(4)
    assert limits.max_keepalive_connections == 1
    assert limits.max_connections == 4


def test_get_network_limits_with_1():
    limits = get_network_limits(1)
    assert limits.max_keepalive_connections == 1
    assert limits.max_connections == 1
