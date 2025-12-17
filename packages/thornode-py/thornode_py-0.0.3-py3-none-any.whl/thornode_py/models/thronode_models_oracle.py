from pydantic import BaseModel


class THORNodeOraclePriceItem(BaseModel):
    symbol: str
    price: str


class THORNodeOraclePrice(BaseModel):
    price: THORNodeOraclePriceItem


class THORNodeOraclePrices(BaseModel):
    prices: list[THORNodeOraclePriceItem]
