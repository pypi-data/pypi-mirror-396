from pydantic import BaseModel
from typing import Optional


class THORNodePool(BaseModel):
    asset: str
    short_code: Optional[str] = None
    status: str
    decimals: Optional[int] = 6
    pending_inbound_asset: str
    pending_inbound_rune: str
    balance_asset: str
    balance_rune: str
    asset_tor_price: str
    pool_units: str
    LP_units: str
    synth_units: str
    synth_supply: str
    savers_depth: str
    savers_units: str
    savers_fill_bps: str
    savers_capacity_remaining: str
    synth_mint_paused: bool
    synth_supply_remaining: str
    loan_collateral: Optional[str] = None
    loan_collateral_remaining: Optional[str] = None
    loan_cr: Optional[str] = None
    derived_depth_bps: str
    trading_halted: bool


class THORNodeDerivedPool(BaseModel):
    asset: str
    status: str
    balance_asset: str
    balance_rune: str
    derived_depth_bps: str
