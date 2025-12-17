import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_oracle import THORNodeOraclePriceItem


@pytest.mark.integration
def test_prices():
    api = THORNodeAPI()

    prices = api.prices().prices
    print(f"test_prices(): Has {len(prices)} prices")
    assert len(prices) > 0

    first = prices[0]
    last = prices[-1]
    print(f"test_prices(): First price {first}")
    print(f"test_prices(): Last price {last}")
    assert isinstance(first, THORNodeOraclePriceItem)
    assert isinstance(last, THORNodeOraclePriceItem)


@pytest.mark.integration
def test_price():
    api = THORNodeAPI()

    symbol = "ETH"
    price = api.price(symbol).price
    print(f"test_price(): Price {price}")
    assert isinstance(price, THORNodeOraclePriceItem)
    assert price.symbol == symbol
