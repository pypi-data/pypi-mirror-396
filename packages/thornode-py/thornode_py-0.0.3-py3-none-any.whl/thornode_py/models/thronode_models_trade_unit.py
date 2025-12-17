from pydantic import BaseModel


class THORNodeTradeUnit(BaseModel):
    asset: str
    units: str
    depth: str
