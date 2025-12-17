from pydantic import BaseModel
from typing import List


class THORNodeTcyStaker(BaseModel):
    address: str
    amount: str


class THORNodeTcyStakersResult(BaseModel):
    tcy_stakers: List[THORNodeTcyStaker]
