from pydantic import BaseModel


class THORNodeBorrower(BaseModel):
    owner: str
    asset: str
    debt_issued: str
    debt_repaid: str
    debt_current: str
    collateral_deposited: str
    collateral_withdrawn: str
    collateral_current: str
    last_open_height: int
    last_repay_height: int
