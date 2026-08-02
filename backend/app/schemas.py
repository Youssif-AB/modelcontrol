from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class TransactionInput(BaseModel):
    transaction_id:str
    date: date
    amount: Decimal
    currency: str
    merchant: str
    category: str
    transaction_type: str
    