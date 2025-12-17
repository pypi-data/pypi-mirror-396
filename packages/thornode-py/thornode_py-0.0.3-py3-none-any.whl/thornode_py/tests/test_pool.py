import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_pool import THORNodePool, THORNodeDerivedPool


@pytest.mark.integration
def test_pools():
    api = THORNodeAPI()

    pools = api.pools()
    print(f"test_pools(): Has {len(pools)} pools")
    assert len(pools) > 0

    first = pools[0]
    last = pools[-1]
    print(f"test_pools(): First pool {first}")
    print(f"test_pools(): Last pool {last}")
    assert isinstance(first, THORNodePool)
    assert isinstance(last, THORNodePool)


@pytest.mark.integration
def test_pool():
    api = THORNodeAPI()

    asset = "ETH.ETH"
    pool = api.pool(asset)
    print(f"test_pool(): Pool {pool}")
    assert isinstance(pool, THORNodePool)
    assert pool.asset == asset


@pytest.mark.integration
def test_dpools():
    api = THORNodeAPI()

    dpools = api.dpools()
    print(f"test_dpools(): Has {len(dpools)} dpools")
    assert len(dpools) > 0

    first = dpools[0]
    last = dpools[-1]
    print(f"test_dpools(): First dpool {first}")
    print(f"test_dpools(): Last dpool {last}")
    assert isinstance(first, THORNodeDerivedPool)
    assert isinstance(last, THORNodeDerivedPool)


@pytest.mark.integration
def test_dpool():
    api = THORNodeAPI()

    asset = "THOR.XRP"
    dpool = api.dpool(asset)
    print(f"test_dpool(): Dpool {dpool}")
    assert isinstance(dpool, THORNodeDerivedPool)
    assert dpool.asset == asset
