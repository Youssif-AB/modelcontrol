from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

class TransactionInput(BaseModel):
    transaction_id:str
    date: date
    amount: Decimal = Field(gt=0)
    currency: str
    merchant: str
    category: str
    transaction_type: Literal["debit","credit"]
