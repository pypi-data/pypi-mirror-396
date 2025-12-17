from pydantic import BaseModel
from typing import List


class THORNodeInvariant(BaseModel):
    invariant: str
    broken: bool
    msg: List[str]


class THORNodeInvariants(BaseModel):
    invariants: List[str]
