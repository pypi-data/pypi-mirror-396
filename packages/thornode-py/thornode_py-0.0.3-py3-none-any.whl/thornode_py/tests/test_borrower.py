import pytest
from thornode_py import THORNodeAPI
from thornode_py.models.thronode_models_borrower import THORNodeBorrower


@pytest.mark.integration
def test_borrowers():
    print("NOT IMPLEMENTED ANY MORE")
    # api = THORNodeAPI()
    #
    # asset = "BTC.BTC"
    # borrowers = api.borrowers(asset)
    # print(f"test_borrowers(): Has {len(borrowers)} borrowers")
    # assert len(borrowers) > 0
    #
    # first = borrowers[0]
    # last = borrowers[-1]
    # print(f"test_borrowers(): First borrower {first}")
    # print(f"test_borrowers(): Last borrower {last}")
    # assert isinstance(first, THORNodeBorrower)
    # assert isinstance(last, THORNodeBorrower)


@pytest.mark.integration
def test_borrower():
    print("NOT IMPLEMENTED ANY MORE")
    # api = THORNodeAPI()
    #
    # asset = "BTC.BTC"
    # borrowers = api.borrowers(asset)
    # first = borrowers[0]
    # borrower = api.borrower(asset, first.owner)
    # print(f"test_borrower(): Borrower {borrower}")
    # assert isinstance(borrower, THORNodeBorrower)
    # assert borrower.owner == first.owner
