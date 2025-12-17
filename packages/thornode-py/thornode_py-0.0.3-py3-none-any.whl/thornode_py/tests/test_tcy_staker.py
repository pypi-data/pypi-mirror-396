import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_tcy_staker import THORNodeTcyStaker


@pytest.mark.integration
def test_tcy_stakers():
    api = THORNodeAPI()

    tcy_stakers = api.tcy_stakers()
    print(f"test_tcy_stakers(): Has {len(tcy_stakers.tcy_stakers)} tcy stakers")
    assert len(tcy_stakers.tcy_stakers) > 0

    first = tcy_stakers.tcy_stakers[0]
    last = tcy_stakers.tcy_stakers[-1]
    print(f"test_tcy_stakers(): First tcy staker {first}")
    print(f"test_tcy_stakers(): Last tcy staker {last}")
    assert isinstance(first, THORNodeTcyStaker)
    assert isinstance(last, THORNodeTcyStaker)


@pytest.mark.integration
def test_tcy_staker():
    api = THORNodeAPI()

    tcy_stakers = api.tcy_stakers()
    first = tcy_stakers.tcy_stakers[0]
    tcy_staker = api.tcy_staker(first.address)
    print(f"test_tcy_staker(): Tcy staker {tcy_staker}")
    assert isinstance(tcy_staker, THORNodeTcyStaker)
    assert tcy_staker.address == first.address
