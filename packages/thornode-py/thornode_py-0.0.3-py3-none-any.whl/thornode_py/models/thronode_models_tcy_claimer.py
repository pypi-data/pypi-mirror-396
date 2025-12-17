from pydantic import BaseModel
from typing import List, Optional


class THORNodeTcyClaimer(BaseModel):
    l1_address: Optional[str] = None
    amount: str
    asset: str


class THORNodeTcyClaimersResult(BaseModel):
    tcy_claimers: List[THORNodeTcyClaimer]


class THORNodeTcyClaimerResult(BaseModel):
    tcy_claimer: List[THORNodeTcyClaimer]
