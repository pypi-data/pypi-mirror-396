import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_health import THORNodePing


@pytest.mark.integration
def test_ping():
    api = THORNodeAPI()

    ping = api.ping()
    print(f"test_ping(): Ping {ping}")
    assert isinstance(ping, THORNodePing)
    assert ping.ping == 'pong'
