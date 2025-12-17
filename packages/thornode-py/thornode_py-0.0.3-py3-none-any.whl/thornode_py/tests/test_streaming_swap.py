import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_streaming_swap import THORNodeStreamingSwap


@pytest.mark.integration
def test_streaming_swaps():
    api = THORNodeAPI()

    swaps = api.streaming_swaps()
    print(f"test_streaming_swaps(): Has {len(swaps)} streaming swaps")
    assert isinstance(swaps, list)
    assert len(swaps) > 0

    first = swaps[0]
    last = swaps[-1]
    print(f"test_streaming_swaps(): First {first}")
    print(f"test_streaming_swaps(): Last {last}")
    assert isinstance(first, THORNodeStreamingSwap)
    assert isinstance(last, THORNodeStreamingSwap)


@pytest.mark.integration
def test_streaming_swap():
    api = THORNodeAPI()

    swaps = api.streaming_swaps()
    first = swaps[0]
    res = api.streaming_swap(first.tx_id)
    print(f"test_streaming_swap(): Result {res}")
    assert isinstance(res, THORNodeStreamingSwap)
    assert res.tx_id == first.tx_id
