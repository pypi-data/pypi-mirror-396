from pydantic import BaseModel


class THORNodePing(BaseModel):
    ping: str
