import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_network import (
    THORNodeNetwork,
    THORNodeOutboundFee,
    THORNodeInboundAddress,
    THORNodeLastBlock,
    THORNodeVersion,
)


@pytest.mark.integration
def test_network():
    api = THORNodeAPI()

    res = api.network()
    print(f"test_network(): Result {res}")
    assert isinstance(res, THORNodeNetwork)


@pytest.mark.integration
def test_outbound_fees():
    api = THORNodeAPI()

    res = api.outbound_fees()
    print(f"test_outbound_fees(): Has {len(res)} fees entries")
    assert isinstance(res, list)
    assert len(res) > 0
    first = res[0]
    last = res[-1]
    print(f"test_outbound_fees(): First {first}")
    print(f"test_outbound_fees(): Last {last}")
    assert isinstance(first, THORNodeOutboundFee)
    assert isinstance(last, THORNodeOutboundFee)


@pytest.mark.integration
def test_outbound_fee():
    api = THORNodeAPI()

    asset = "ETH.ETH"
    res = api.outbound_fee(asset)
    print(f"test_outbound_fee(): Result {res}")
    assert isinstance(res[0], THORNodeOutboundFee)
    assert res[0].asset == asset


@pytest.mark.integration
def test_inbound_addresses():
    api = THORNodeAPI()

    res = api.inbound_addresses()
    print(f"test_inbound_addresses(): Has {len(res)} inbound addresses")
    assert isinstance(res, list)
    assert len(res) > 0
    first = res[0]
    last = res[-1]
    print(f"test_inbound_addresses(): First {first}")
    print(f"test_inbound_addresses(): Last {last}")
    assert isinstance(first, THORNodeInboundAddress)
    assert isinstance(last, THORNodeInboundAddress)


@pytest.mark.integration
def test_lastblock():
    api = THORNodeAPI()

    res = api.lastblock()
    print(f"test_lastblock(): Has {len(res)} entries")
    assert isinstance(res, list)
    assert len(res) > 0
    first = res[0]
    last = res[-1]
    print(f"test_lastblock(): First {first}")
    print(f"test_lastblock(): Last {last}")
    assert isinstance(first, THORNodeLastBlock)
    assert isinstance(last, THORNodeLastBlock)


@pytest.mark.integration
def test_lastblock_chain():
    api = THORNodeAPI()

    chain = "BTC"
    res = api.lastblock_chain(chain)
    print(f"test_lastblock_chain(): Result {res}")
    assert isinstance(res[0], THORNodeLastBlock)
    assert res[0].chain == chain


@pytest.mark.integration
def test_version():
    api = THORNodeAPI()

    res = api.version()
    print(f"test_version(): Result {res}")
    assert isinstance(res, THORNodeVersion)
    assert isinstance(res.current, str)
    assert len(res.current) > 0
