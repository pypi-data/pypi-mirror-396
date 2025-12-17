from pydantic import BaseModel
from typing import Optional


class THORNodePoolSlip(BaseModel):
    asset: str
    pool_slip: int
    rollup_count: int
    long_rollup: int
    rollup: int
    summed_rollup: Optional[int] = None
