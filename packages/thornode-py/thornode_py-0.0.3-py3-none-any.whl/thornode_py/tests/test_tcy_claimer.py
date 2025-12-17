import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_tcy_claimer import THORNodeTcyClaimer, THORNodeTcyClaimerResult


@pytest.mark.integration
def test_tcy_claimers():
    api = THORNodeAPI()

    tcy_claimers = api.tcy_claimers()
    print(f"test_tcy_claimers(): Has {len(tcy_claimers.tcy_claimers)} tcy claimers")
    assert len(tcy_claimers.tcy_claimers) > 0

    first = tcy_claimers.tcy_claimers[0]
    last = tcy_claimers.tcy_claimers[-1]
    print(f"test_tcy_claimers(): First tcy claimer {first}")
    print(f"test_tcy_claimers(): Last tcy claimer {last}")
    assert isinstance(first, THORNodeTcyClaimer)
    assert isinstance(last, THORNodeTcyClaimer)


@pytest.mark.integration
def test_tcy_claimer():
    api = THORNodeAPI()

    tcy_claimers = api.tcy_claimers()
    first = tcy_claimers.tcy_claimers[0]
    tcy_claimer = api.tcy_claimer(first.l1_address)
    print(f"test_tcy_claimer(): Tcy claimer {tcy_claimer}")
    assert isinstance(tcy_claimer, THORNodeTcyClaimerResult)
    assert tcy_claimer.tcy_claimer[0].l1_address == first.l1_address
