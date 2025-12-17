from pydantic import BaseModel
from typing import List, Optional


class THORNodeStreamingSwap(BaseModel):
    tx_id: Optional[str] = None
    interval: Optional[int] = None
    quantity: Optional[int] = None
    count: Optional[int] = None
    last_height: Optional[int] = None
    trade_target: str
    source_asset: Optional[str] = None
    target_asset: Optional[str] = None
    destination: Optional[str] = None
    deposit: str
    in_: str
    out: str
    failed_swaps: Optional[List[int]] = None
    failed_swap_reasons: Optional[List[str]] = None

    # map JSON field "in" to Python-safe attribute in_
    @classmethod
    def model_validate(cls, obj):
        if isinstance(obj, dict) and "in" in obj:
            obj = dict(obj)
            obj["in_"] = obj.pop("in")
        return super().model_validate(obj)
