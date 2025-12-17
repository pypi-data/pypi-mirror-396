from pydantic import BaseModel
from typing import Optional


class THORNodeQuoteFees(BaseModel):
    asset: str
    affiliate: Optional[str] = None
    outbound: Optional[str] = None
    liquidity: str
    total: str
    slippage_bps: int
    total_bps: int


class THORNodeQuoteBase(BaseModel):
    inbound_address: Optional[str] = None
    inbound_confirmation_blocks: Optional[int] = None
    inbound_confirmation_seconds: Optional[int] = None
    outbound_delay_blocks: Optional[int] = None
    outbound_delay_seconds: Optional[int] = None
    fees: Optional[THORNodeQuoteFees] = None
    router: Optional[str] = None
    expiry: Optional[int] = None
    warning: Optional[str] = None
    notes: Optional[str] = None
    dust_threshold: Optional[str] = None
    recommended_min_amount_in: Optional[str] = None
    recommended_gas_rate: Optional[str] = None
    gas_rate_units: Optional[str] = None


class THORNodeQuoteSwap(THORNodeQuoteBase):
    memo: Optional[str] = None
    expected_amount_out: str
    max_streaming_quantity: Optional[int] = None
    streaming_swap_blocks: Optional[int] = None
    streaming_swap_seconds: Optional[int] = None
    total_swap_seconds: Optional[int] = None


class THORNodeQuoteSaverDeposit(THORNodeQuoteBase):
    memo: str
    expected_amount_out: Optional[str] = None
    expected_amount_deposit: str
    slippage_bps: Optional[int] = None


class THORNodeQuoteSaverWithdraw(THORNodeQuoteBase):
    memo: str
    dust_amount: str
    expected_amount_out: str
    slippage_bps: Optional[int] = None


class THORNodeQuoteLoanOpen(THORNodeQuoteBase):
    memo: Optional[str] = None
    expected_amount_out: str
    expected_collateralization_ratio: str
    expected_collateral_deposited: str
    expected_debt_issued: str
    streaming_swap_blocks: int
    streaming_swap_seconds: int
    total_open_loan_seconds: int


class THORNodeQuoteLoanClose(THORNodeQuoteBase):
    memo: Optional[str] = None
    expected_amount_out: str
    expected_amount_in: str
    expected_collateral_withdrawn: str
    expected_debt_repaid: str
    streaming_swap_blocks: int
    streaming_swap_seconds: int
    total_repay_seconds: int
