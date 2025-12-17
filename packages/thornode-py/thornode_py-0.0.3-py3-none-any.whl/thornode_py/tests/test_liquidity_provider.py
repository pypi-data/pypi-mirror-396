import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_liquidiry_provider import THORNodeLiquidityProviderSummary, THORNodeLiquidityProvider


@pytest.mark.integration
def test_liquidity_providers():
    api = THORNodeAPI()

    asset = "ETH.ETH"
    liquidity_providers = api.liquidity_providers(asset)
    print(f"test_liquidity_providers(): Has {len(liquidity_providers)} liquidity providers")
    assert len(liquidity_providers) > 0

    first = liquidity_providers[0]
    last = liquidity_providers[-1]
    print(f"test_liquidity_providers(): First liquidity provider {first}")
    print(f"test_liquidity_providers(): Last liquidity provider {last}")
    assert isinstance(first, THORNodeLiquidityProviderSummary)
    assert isinstance(last, THORNodeLiquidityProviderSummary)


@pytest.mark.integration
def test_liquidity_provider():
    api = THORNodeAPI()

    asset = "ETH.ETH"
    liquidity_providers = api.liquidity_providers(asset)
    first = liquidity_providers[0]
    liquidity_provider = api.liquidity_provider(asset, first.asset_address)
    print(f"test_node(): Liquidity provider {liquidity_provider}")
    assert isinstance(liquidity_provider, THORNodeLiquidityProvider)
    assert liquidity_provider.asset_address == first.asset_address
