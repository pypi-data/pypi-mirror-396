from pydantic import BaseModel
from typing import List, Optional


class THORNodeNetwork(BaseModel):
    bond_reward_rune: str
    total_bond_units: str
    available_pools_rune: str
    vaults_liquidity_rune: str
    effective_security_bond: str
    total_reserve: str
    vaults_migrating: bool
    gas_spent_rune: str
    gas_withheld_rune: str
    native_outbound_fee_rune: str
    native_tx_fee_rune: str
    tns_register_fee_rune: str
    tns_fee_per_block_rune: str
    rune_price_in_tor: str
    tor_price_in_rune: str
    tor_price_halted: bool
    # Optional fields present in schema but not required
    outbound_fee_multiplier: Optional[str] = None


class THORNodeOutboundFee(BaseModel):
    asset: str
    outbound_fee: str
    fee_withheld_rune: Optional[str] = None
    fee_spent_rune: Optional[str] = None
    surplus_rune: Optional[str] = None
    dynamic_multiplier_basis_points: Optional[str] = None


class THORNodeInboundAddress(BaseModel):
    chain: Optional[str] = None
    pub_key: Optional[str] = None
    address: Optional[str] = None
    router: Optional[str] = None
    halted: bool
    global_trading_paused: bool
    chain_trading_paused: bool
    chain_lp_actions_paused: bool
    observed_fee_rate: Optional[str] = None
    gas_rate: Optional[str] = None
    gas_rate_units: Optional[str] = None
    outbound_tx_size: Optional[str] = None
    outbound_fee: Optional[str] = None
    dust_threshold: Optional[str] = None


class THORNodeLastBlock(BaseModel):
    chain: str
    last_observed_in: int
    last_signed_out: int
    thorchain: int


class THORNodeVersion(BaseModel):
    current: str
    next: str
    querier: str
    next_since_height: Optional[int] = None
