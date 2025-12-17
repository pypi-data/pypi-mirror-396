import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_thorname import THORNodeThorname


@pytest.mark.integration
def test_thorname():
    api = THORNodeAPI()

    name = "rapidoswaps"
    thorname = api.thorname(name)
    print(f"test_balances(): Thorname {thorname}")
    assert isinstance(thorname, THORNodeThorname)
    assert thorname.owner == "thor1c2ej2t59upl2mwky9hj2y20wdst5gklyzpc4m4"
    assert len(thorname.aliases) > 0
