from fastapi import FastAPI, UploadFile
from app.schemas import ModelCreate


app = FastAPI(title="ModelControl API")

@app.get("/health")
def health_check() -> dict[str,str]:
    return {"status":"ok"}

@app.post("/models/validate")
def validate_model(model: ModelCreate) -> ModelCreate:
    return model



