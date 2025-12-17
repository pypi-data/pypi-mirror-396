import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_swap import THORNodeSwapDetailsResponse


@pytest.mark.integration
def test_queue_swap_details():
    api = THORNodeAPI()

    tx_id = "106EEB6CEC120D3CE4A88F653DF2402D1E2DC4FC2B73E1531CAD49D0619A443A"
    res = api.queue_swap_details(tx_id)
    print(f"test_queue_swap_details(): Result {res}")
    assert isinstance(res, THORNodeSwapDetailsResponse)
    assert res.swap.tx.id.upper() == tx_id.upper()
