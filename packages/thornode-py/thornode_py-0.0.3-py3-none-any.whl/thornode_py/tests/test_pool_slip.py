import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_pool_slip import THORNodePoolSlip


@pytest.mark.integration
def test_slips():
    api = THORNodeAPI()

    slips = api.slips()
    print(f"test_slips(): Has {len(slips)} slips")
    assert len(slips) > 0

    first = slips[0]
    last = slips[-1]
    print(f"test_slips(): First slip {first}")
    print(f"test_slips(): Last slip {last}")
    assert isinstance(first, THORNodePoolSlip)
    assert isinstance(last, THORNodePoolSlip)


@pytest.mark.integration
def test_slip():
    api = THORNodeAPI()

    asset = "ETH.ETH"
    slip = api.slip(asset)
    print(f"test_slip(): Slip {slip}")
    assert len(slip) == 1
    slip = slip[0]
    assert isinstance(slip, THORNodePoolSlip)
    assert slip.asset == asset
