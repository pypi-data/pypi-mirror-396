import pytest
import requests
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_node import THORNodeNode


@pytest.mark.integration
def test_nodes():
    api = THORNodeAPI()

    # Get nodes
    nodes = api.nodes()
    print(f"test_nodes(): Has {len(nodes)} nodes")
    assert len(nodes) > 0

    # Check first/last nodes
    first = nodes[0]
    last = nodes[-1]
    print(f"test_nodes(): First node {first}")
    print(f"test_nodes(): Last node {last}")
    assert isinstance(first, THORNodeNode)
    assert isinstance(last, THORNodeNode)


@pytest.mark.integration
def test_node():
    api = THORNodeAPI()

    # Get first node
    nodes = api.nodes()
    first = nodes[0]
    node = api.node(first.node_address)
    print(f"test_node(): Node {node}")
    assert isinstance(node, THORNodeNode)


@pytest.mark.integration
def test_node_invalid_address():
    api = THORNodeAPI()

    # Get invalid node
    with pytest.raises(requests.exceptions.HTTPError):
        node = api.node("xxx")
