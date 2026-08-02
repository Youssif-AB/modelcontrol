from fastapi import FastAPI, UploadFile
from app.schemas import TransactionInput


app = FastAPI(title="TransactScope API")

@app.get("/health")
def health_check() -> dict[str,str]:
    return {"status":"ok"}

@app.post("/transactions/validate")
def validate_transaction(transaction: TransactionInput) -> TransactionInput:
    return transaction

@app.post("/transactions/upload")
def upload_transactions(file: UploadFile) -> dict[str, str | None]:
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
