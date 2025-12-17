from pydantic import BaseModel


class THORNodeSecuredAsset(BaseModel):
    asset: str
    supply: str
    depth: str
