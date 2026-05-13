from fastapi import FastAPI
from pydantic import BaseModel
from agent import CodeAnalysisAgent
from fastapi.middleware.cors import CORSMiddleware
import time
from analyzer import fix_code
from fastapi import UploadFile, File
from project_analyzer import analyze_project

app = FastAPI()
agent = CodeAnalysisAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
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
    return agent.process(request.code)

@app.post("/fix")
def fix(request: CodeRequest):
    print(f"Fix endpoint çağrıldı | Kod uzunluğu: {len(request.code)} karakter")
    return fix_code(request.code)

@app.post("/analyze-project")
async def analyze_project_files(files: list[UploadFile] = File(...)):
    uploaded_files = []

    for file in files:
        if not file.filename.endswith(".py"):
            continue

        content = await file.read()
        code = content.decode("utf-8", errors="ignore")

        uploaded_files.append({
            "filename": file.filename,
            "content": code
        })

    if not uploaded_files:
        return {
            "status": "error",
            "message": "Analiz edilecek Python dosyası bulunamadı."
        }

    return analyze_project(uploaded_files)