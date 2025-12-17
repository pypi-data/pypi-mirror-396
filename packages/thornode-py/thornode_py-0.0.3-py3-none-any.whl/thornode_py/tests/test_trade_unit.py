import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_trade_unit import THORNodeTradeUnit


@pytest.mark.integration
def test_trade_units():
    api = THORNodeAPI()

    res = api.trade_units()
    print(f"test_trade_units(): Has {len(res)} trade units entries")
    assert isinstance(res, list)
    assert len(res) > 0
    first = res[0]
    last = res[-1]
    print(f"test_trade_units(): First {first}")
    print(f"test_trade_units(): Last {last}")
    assert isinstance(first, THORNodeTradeUnit)
    assert isinstance(last, THORNodeTradeUnit)


@pytest.mark.integration
def test_trade_unit():
    api = THORNodeAPI()

    all_units = api.trade_units()
    first = all_units[0]
    asset = first.asset
    result = api.trade_unit(asset)
    print(f"test_trade_unit(): Result {result}")
    assert isinstance(result, THORNodeTradeUnit)
    assert result.asset == asset
