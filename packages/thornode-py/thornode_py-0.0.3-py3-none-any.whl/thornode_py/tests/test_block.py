import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_block import THORNodeBlock


@pytest.mark.integration
def test_block():
    api = THORNodeAPI()

    res = api.block()
    print(f"test_block(): Result {res}")
    assert isinstance(res, THORNodeBlock)
    assert isinstance(res.header.height, int)
    # Events arrays should be present (can be empty)
    assert isinstance(res.begin_block_events, list)
    assert isinstance(res.end_block_events, list)
    assert isinstance(res.finalize_block_events, list)
    assert isinstance(res.txs, list)
