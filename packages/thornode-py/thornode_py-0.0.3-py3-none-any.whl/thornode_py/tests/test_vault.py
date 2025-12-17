import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_vault import (
    THORNodeVault,
    THORNodeVaultYggdrasil,
    THORNodeVaultPubkeysResponse,
)


@pytest.mark.integration
def test_vaults_asgard():
    api = THORNodeAPI()

    vaults = api.vaults_asgard()
    print(f"test_vaults_asgard(): Has {len(vaults)} asgard vaults")
    assert len(vaults) > 0

    first = vaults[0]
    last = vaults[-1]
    print(f"test_vaults_asgard(): First asgard vault {first}")
    print(f"test_vaults_asgard(): Last asgard vault {last}")
    assert isinstance(first, THORNodeVault)
    assert isinstance(last, THORNodeVault)


@pytest.mark.integration
def test_vault():
    api = THORNodeAPI()

    asgard = api.vaults_asgard()
    first = asgard[0]
    v = api.vault(first.pub_key)
    print(f"test_vault(): Vault {v}")
    assert isinstance(v, THORNodeVault)
    assert v.pub_key == first.pub_key


@pytest.mark.integration
def test_vault_pubkeys():
    api = THORNodeAPI()

    res = api.vault_pubkeys()
    print(f"test_vault_pubkeys(): Result {res}")
    assert isinstance(res, THORNodeVaultPubkeysResponse)
    assert isinstance(res.asgard, list)
    assert len(res.asgard) > 0
