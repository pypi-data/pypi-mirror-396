from pydantic import BaseModel
from typing import Optional


class THORNodeSaver(BaseModel):
    asset: str
    asset_address: str
    units: str
    asset_deposit_value: str
    asset_redeem_value: str
    growth_pct: str
    last_add_height: Optional[int] = None
    last_withdraw_height: Optional[int] = None
