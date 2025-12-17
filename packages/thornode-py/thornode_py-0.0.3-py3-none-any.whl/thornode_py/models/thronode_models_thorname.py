from pydantic import BaseModel
from typing import List


class THORNodeThornameAlias(BaseModel):
    chain: str
    address: str


class THORNodeThorname(BaseModel):
    name: str
    expire_block_height: int
    owner: str
    preferred_asset: str
    preferred_asset_swap_threshold_rune: str
    affiliate_collector_rune: str
    aliases: List[THORNodeThornameAlias]
