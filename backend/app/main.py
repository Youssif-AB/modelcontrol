from fastapi import FastAPI, UploadFile
from app.schemas import TransactionInput


app = FastAPI(title="ModelControl API")

@app.get("/health")
def health_check() -> dict[str,str]:
    return {"status":"ok"}

