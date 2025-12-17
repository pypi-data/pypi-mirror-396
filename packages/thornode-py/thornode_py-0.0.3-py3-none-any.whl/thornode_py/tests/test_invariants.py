import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_invariant import THORNodeInvariant, THORNodeInvariants


@pytest.mark.integration
def test_invariants():
    api = THORNodeAPI()

    res = api.invariants()
    print(f"test_invariants(): Result {res}")
    assert isinstance(res, THORNodeInvariants)
    assert isinstance(res.invariants, list)


@pytest.mark.integration
def test_invariant():
    api = THORNodeAPI()

    invariants = api.invariants()
    name = invariants.invariants[0]
    inv = api.invariant(name)
    print(f"test_invariant(): Invariant {inv}")
    assert isinstance(inv, THORNodeInvariant)
    assert inv.invariant == name
    assert isinstance(inv.broken, bool)
