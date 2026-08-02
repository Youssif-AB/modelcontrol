from fastapi import FastAPI
from app.schemas import TransactionInput

app = FastAPI(title="TransactScope API")

@app.get("/health")
def health_check() -> dict[str,str]:
    return {"status":"ok"}

@app.post("/transactions/validate")
def validate_transaction(transaction: TransactionInput) -> TransactionInput:
    return transaction
