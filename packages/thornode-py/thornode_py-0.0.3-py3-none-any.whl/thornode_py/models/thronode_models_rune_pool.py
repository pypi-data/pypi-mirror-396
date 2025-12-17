from pydantic import BaseModel


class THORNodeRunePoolPol(BaseModel):
    rune_deposited: str
    rune_withdrawn: str
    value: str
    pnl: str
    current_deposit: str


class THORNodeRunePoolProviders(BaseModel):
    units: str
    pending_units: str
    pending_rune: str
    value: str
    pnl: str
    current_deposit: str


class THORNodeRunePoolReserve(BaseModel):
    units: str
    value: str
    pnl: str
    current_deposit: str


class THORNodeRunePool(BaseModel):
    pol: THORNodeRunePoolPol
    providers: THORNodeRunePoolProviders
    reserve: THORNodeRunePoolReserve


class THORNodeRuneProvider(BaseModel):
    rune_address: str
    units: str
    value: str
    pnl: str
    deposit_amount: str
    withdraw_amount: str
    last_deposit_height: int
    last_withdraw_height: int
