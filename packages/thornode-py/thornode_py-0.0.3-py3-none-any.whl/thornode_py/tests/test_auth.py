import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_auth import THORNodeAccountsResponse


@pytest.mark.integration
def test_accounts():
    api = THORNodeAPI()

    hash = "thor1c2ej2t59upl2mwky9hj2y20wdst5gklyzpc4m4"
    accounts = api.accounts(hash)
    print(f"test_ping(): Accounts {accounts}")
    assert isinstance(accounts, THORNodeAccountsResponse)
    assert accounts.result.value.address == hash
