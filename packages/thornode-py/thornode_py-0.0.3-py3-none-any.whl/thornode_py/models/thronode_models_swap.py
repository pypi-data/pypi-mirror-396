from pydantic import BaseModel
from typing import List, Optional
from .thronode_models_transaction import THORNodeTx


class THORNodeSwapState(BaseModel):
    interval: Optional[int] = None
    quantity: Optional[int] = None
    ttl: Optional[int] = None
    count: Optional[int] = None
    last_height: Optional[int] = None
    deposit: Optional[str] = None
    withdrawn: Optional[str] = None
    in_: Optional[str] = None
    out: Optional[str] = None
    failed_swaps: Optional[List[int]] = None
    failed_swap_reasons: Optional[List[str]] = None

    @classmethod
    def model_validate(cls, obj):
        if isinstance(obj, dict) and "in" in obj:
            obj = dict(obj)
            obj["in_"] = obj.pop("in")
        return super().model_validate(obj)


class THORNodeMsgSwap(BaseModel):
    tx: THORNodeTx
    target_asset: str
    destination: Optional[str] = None
    trade_target: str
    affiliate_address: Optional[str] = None
    affiliate_basis_points: str
    signer: Optional[str] = None
    aggregator: Optional[str] = None
    aggregator_target_address: Optional[str] = None
    aggregator_target_limit: Optional[str] = None
    swap_type: Optional[str] = None
    stream_quantity: Optional[int] = None
    stream_interval: Optional[int] = None
    initial_block_height: Optional[int] = None
    state: Optional[THORNodeSwapState] = None
    version: Optional[str] = None
    index: Optional[int] = None


class THORNodeSwapDetailsResponse(BaseModel):
    swap: Optional[THORNodeMsgSwap] = None
    status: Optional[str] = None
    queue_type: Optional[str] = None
