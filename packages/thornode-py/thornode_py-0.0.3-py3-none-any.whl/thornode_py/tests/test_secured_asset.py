import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_secured_asset import THORNodeSecuredAsset


@pytest.mark.integration
def test_secured_assets():
    api = THORNodeAPI()

    res = api.secured_assets()
    print(f"test_secured_assets(): Has {len(res)} secured assets entries")
    assert isinstance(res, list)
    assert len(res) > 0
    first = res[0]
    last = res[-1]
    print(f"test_secured_assets(): First {first}")
    print(f"test_secured_assets(): Last {last}")
    assert isinstance(first, THORNodeSecuredAsset)
    assert isinstance(last, THORNodeSecuredAsset)


@pytest.mark.integration
def test_secured_asset():
    api = THORNodeAPI()

    all_assets = api.secured_assets()
    first = all_assets[0]
    asset = first.asset
    result = api.secured_asset(asset)
    print(f"test_secured_asset(): Result {result}")
    assert isinstance(result, THORNodeSecuredAsset)
    assert result.asset == asset
