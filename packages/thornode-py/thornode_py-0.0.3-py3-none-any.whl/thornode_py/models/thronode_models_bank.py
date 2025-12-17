from pydantic import BaseModel
from typing import List


class THORNodeBalanceAmount(BaseModel):
    denom: str
    amount: str


class THORNodeBalancesResponse(BaseModel):
    result: List[THORNodeBalanceAmount]
