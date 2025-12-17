import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_bank import THORNodeBalancesResponse


@pytest.mark.integration
def test_balances():
    api = THORNodeAPI()

    hash = "thor1c2ej2t59upl2mwky9hj2y20wdst5gklyzpc4m4"
    balances = api.balances(hash)
    print(f"test_balances(): Balances {balances}")
    assert isinstance(balances, THORNodeBalancesResponse)
    assert len(balances.result) > 0
