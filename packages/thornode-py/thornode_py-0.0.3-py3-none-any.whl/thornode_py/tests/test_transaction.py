import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_transaction import (
    THORNodeTxResponse,
    THORNodeTxDetailsResponse,
    THORNodeTxStagesResponse,
    THORNodeTxStatusResponse,
)


TX_HASH = "F36B55F28EA108E015FDDDB1CC310A37C9893A39D4E1A1C8068EDDCB682155C5"


@pytest.mark.integration
def test_tx():
    api = THORNodeAPI()

    result = api.tx(TX_HASH)
    print(f"test_tx(): Tx {result}")
    assert isinstance(result, THORNodeTxResponse)


@pytest.mark.integration
def test_tx_signers():
    api = THORNodeAPI()

    result = api.tx_signers(TX_HASH)
    print(f"test_tx_signers(): Tx signers {result}")
    assert isinstance(result, THORNodeTxDetailsResponse)


@pytest.mark.integration
def test_tx_details():
    api = THORNodeAPI()

    result = api.tx_details(TX_HASH)
    print(f"test_tx_details(): Tx details {result}")
    assert isinstance(result, THORNodeTxDetailsResponse)


@pytest.mark.integration
def test_tx_stages():
    api = THORNodeAPI()

    result = api.tx_stages(TX_HASH)
    print(f"test_tx_stages(): Tx stages {result}")
    assert isinstance(result, THORNodeTxStagesResponse)


@pytest.mark.integration
def test_tx_status():
    api = THORNodeAPI()

    result = api.tx_status(TX_HASH)
    print(f"test_tx_status(): Tx status {result}")
    assert isinstance(result, THORNodeTxStatusResponse)
