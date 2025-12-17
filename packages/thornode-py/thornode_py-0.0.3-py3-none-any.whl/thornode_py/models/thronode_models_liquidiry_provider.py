from pydantic import BaseModel
from typing import Optional


class THORNodeLiquidityProviderSummary(BaseModel):
    asset: str
    units: str
    pending_rune: str
    pending_asset: str
    rune_deposit_value: str
    asset_deposit_value: str
    rune_address: Optional[str] = None
    asset_address: Optional[str] = None
    last_add_height: Optional[int] = None
    last_withdraw_height: Optional[int] = None
    pending_tx_id: Optional[str] = None


class THORNodeLiquidityProvider(BaseModel):
    asset: str
    units: str
    pending_rune: str
    pending_asset: str
    rune_deposit_value: str
    asset_deposit_value: str
    rune_address: Optional[str] = None
    asset_address: Optional[str] = None
    last_add_height: Optional[int] = None
    last_withdraw_height: Optional[int] = None
    pending_tx_id: Optional[str] = None
    rune_redeem_value: Optional[str] = None
    asset_redeem_value: Optional[str] = None
    luvi_deposit_value: Optional[str] = None
    luvi_redeem_value: Optional[str] = None
    luvi_growth_pct: Optional[str] = None
