from decimal import Decimal
from pydantic import BaseModel

class TransferRequest(BaseModel):
    amount: Decimal
    to_account_id: int

class AccountResponse(BaseModel):
    id: int
    balance: Decimal
    user_id: int

    class Config:
        from_attributes = True