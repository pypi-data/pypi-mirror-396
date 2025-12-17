import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_quote import (
    THORNodeQuoteSwap,
    THORNodeQuoteSaverDeposit,
    THORNodeQuoteSaverWithdraw,
    THORNodeQuoteLoanOpen,
    THORNodeQuoteLoanClose,
)


@pytest.mark.integration
def test_quote_swap():
    api = THORNodeAPI()

    res = api.quote_swap(
        from_asset="BTC.BTC",
        to_asset="ETH.ETH",
        amount=100000,
        destination="0x1c7b17362c84287bd1184447e6dfeaf920c31bbe",
    )
    print(f"test_quote_swap(): Result {res}")
    assert isinstance(res, THORNodeQuoteSwap)
    assert isinstance(res.fees.asset, str)


# @pytest.mark.integration
# def test_quote_saver_deposit():
#     api = THORNodeAPI()
#
#     res = api.quote_saver_deposit(asset="BTC.BTC", amount=100000)
#     print(f"test_quote_saver_deposit(): Result {res}")
#     assert isinstance(res, THORNodeQuoteSaverDeposit)
#
#
# @pytest.mark.integration
# def test_quote_saver_withdraw():
#     api = THORNodeAPI()
#
#     # Try to find a real saver to avoid flakiness
#     try:
#         savers = api.savers("BTC.BTC")
#     except Exception:
#         savers = []
#     if len(savers) == 0:
#         pytest.skip("No savers available to test saver withdraw quote")
#     addr = savers[0].asset_address
#     res = api.quote_saver_withdraw(asset="BTC.BTC", address=addr, withdraw_bps=100)
#     print(f"test_quote_saver_withdraw(): Result {res}")
#     assert isinstance(res, THORNodeQuoteSaverWithdraw)
#
#
# @pytest.mark.integration
# def test_quote_loan_open():
#     api = THORNodeAPI()
#
#     res = api.quote_loan_open(
#         from_asset="BTC.BTC",
#         amount=100000,
#         to_asset="ETH.ETH",
#         destination="0x1c7b17362c84287bd1184447e6dfeaf920c31bbe",
#     )
#     print(f"test_quote_loan_open(): Result {res}")
#     assert isinstance(res, THORNodeQuoteLoanOpen)
#
#
# @pytest.mark.integration
# def test_quote_loan_close():
#     api = THORNodeAPI()
#
#     # Find a borrower to use as loan_owner if available
#     try:
#         borrowers = api.borrowers("BTC.BTC")
#     except Exception:
#         borrowers = []
#     if len(borrowers) == 0:
#         pytest.skip("No borrowers available to test loan close quote")
#     owner = borrowers[0].owner
#     res = api.quote_loan_close(
#         from_asset="ETH.ETH",
#         repay_bps=100,
#         to_asset="BTC.BTC",
#         loan_owner=owner,
#     )
#     print(f"test_quote_loan_close(): Result {res}")
#     assert isinstance(res, THORNodeQuoteLoanClose)
