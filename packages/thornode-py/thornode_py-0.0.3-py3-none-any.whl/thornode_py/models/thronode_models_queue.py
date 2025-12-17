from pydantic import BaseModel


class THORNodeQueue(BaseModel):
    swap: int
    outbound: int
    internal: int
    scheduled_outbound_value: str
    scheduled_outbound_clout: str
