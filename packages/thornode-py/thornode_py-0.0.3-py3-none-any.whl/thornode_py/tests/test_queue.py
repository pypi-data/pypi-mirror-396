import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_queue import THORNodeQueue
from thornode_py.models.thronode_models_swap import THORNodeMsgSwap
from thornode_py.models.thronode_models_transaction import THORNodeTxAction


@pytest.mark.integration
def test_queue():
    api = THORNodeAPI()

    res = api.queue()
    print(f"test_queue(): Result {res}")
    assert isinstance(res, THORNodeQueue)


@pytest.mark.integration
def test_queue_swap():
    api = THORNodeAPI()

    res = api.queue_swap()
    print(f"test_queue_swap(): Has {len(res)} items")
    assert isinstance(res, list)
    if len(res) > 0:
        first = res[0]
        last = res[-1]
        print(f"test_queue_swap(): First {first}")
        print(f"test_queue_swap(): Last {last}")
        assert isinstance(first, THORNodeMsgSwap)
        assert isinstance(last, THORNodeMsgSwap)


@pytest.mark.integration
def test_queue_outbound():
    api = THORNodeAPI()

    res = api.queue_outbound()
    print(f"test_queue_outbound(): Has {len(res)} items")
    assert isinstance(res, list)
    if len(res) > 0:
        first = res[0]
        last = res[-1]
        print(f"test_queue_outbound(): First {first}")
        print(f"test_queue_outbound(): Last {last}")
        assert isinstance(first, THORNodeTxAction)
        assert isinstance(last, THORNodeTxAction)
