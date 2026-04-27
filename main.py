from fastapi import FastAPI
from pydantic import BaseModel
from analyzer import analyze_code

app = FastAPI()


class CodeRequest(BaseModel):
    code: str


@app.get("/")
def home():
    return {"message": "Backend çalışıyor 🚀"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Code analyzer backend aktif çalışıyor."
    }


@app.post("/analyze")
def analyze(request: CodeRequest):
    return analyze_code(request.code)