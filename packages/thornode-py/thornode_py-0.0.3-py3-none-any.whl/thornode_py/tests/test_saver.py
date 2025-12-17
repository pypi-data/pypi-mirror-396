import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_saver import THORNodeSaver


@pytest.mark.integration
def test_savers():
    api = THORNodeAPI()

    asset = "BTC.BTC"
    savers = api.savers(asset)
    print(f"test_savers(): Has {len(savers)} savers")
    assert len(savers) > 0

    first = savers[0]
    last = savers[-1]
    print(f"test_savers(): First saver {first}")
    print(f"test_savers(): Last saver {last}")
    assert isinstance(first, THORNodeSaver)
    assert isinstance(last, THORNodeSaver)


@pytest.mark.integration
def test_saver():
    api = THORNodeAPI()

    asset = "BTC.BTC"
    savers = api.savers(asset)
    first = savers[0]
    saver = api.saver(asset, first.asset_address)
    print(f"test_saver(): Saver {saver}")
    assert isinstance(saver, THORNodeSaver)
    assert saver.asset_address == first.asset_address
