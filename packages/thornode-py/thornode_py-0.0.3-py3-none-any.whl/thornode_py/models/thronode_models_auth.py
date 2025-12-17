from pydantic import BaseModel


class THORNodeAccount(BaseModel):
    address: str
    pub_key: str
    account_number: str
    sequence: str


class THORNodeAccountResult(BaseModel):
    value: THORNodeAccount


class THORNodeAccountsResponse(BaseModel):
    result: THORNodeAccountResult
