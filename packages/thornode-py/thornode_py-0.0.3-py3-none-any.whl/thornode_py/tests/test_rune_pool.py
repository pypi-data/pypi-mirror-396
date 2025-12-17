import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_rune_pool import THORNodeRunePool, THORNodeRuneProvider


@pytest.mark.integration
def test_runepool():
    api = THORNodeAPI()

    runepool = api.runepool()
    print(f"test_runepool(): Runepool {runepool}")
    assert isinstance(runepool, THORNodeRunePool)


@pytest.mark.integration
def test_rune_providers():
    api = THORNodeAPI()

    rune_providers = api.rune_providers()
    print(f"test_rune_providers(): Has {len(rune_providers)} rune providers")
    assert len(rune_providers) > 0

    first = rune_providers[0]
    last = rune_providers[-1]
    print(f"test_rune_providers(): First rune provider {first}")
    print(f"test_rune_providers(): Last rune provider {last}")
    assert isinstance(first, THORNodeRuneProvider)
    assert isinstance(last, THORNodeRuneProvider)


@pytest.mark.integration
def test_rune_provider():
    api = THORNodeAPI()

    rune_providers = api.rune_providers()
    first = rune_providers[0]
    rune_provider = api.rune_provider(first.rune_address)
    print(f"test_rune_provider(): Rune provider {rune_provider}")
    assert isinstance(rune_provider, THORNodeRuneProvider)
    assert rune_provider.rune_address == first.rune_address
