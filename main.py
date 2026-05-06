from fastapi import FastAPI
from pydantic import BaseModel
from analyzer import analyze_code
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    print(f"Analyze endpoint çağrıldı | Kod uzunluğu: {len(request.code)} karakter")
    time.sleep(2)
    return analyze_code(request.code)
