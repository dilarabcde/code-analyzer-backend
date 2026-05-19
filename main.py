from fastapi import FastAPI
from pydantic import BaseModel
from agent import CodeAnalysisAgent
from fastapi.middleware.cors import CORSMiddleware
import time
from analyzer import fix_code
from fastapi import UploadFile, File
from project_analyzer import analyze_project
from llm_service import get_llm_analysis
from multi_language_analyzer import (analyze_cpp_code,analyze_javascript_code,
    analyze_java_code,analyze_go_code)

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
    language: str = "python"


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
    print(
        f"Analyze endpoint çağrıldı | Dil: {request.language} | Kod uzunluğu: {len(request.code)} karakter"
    )

    time.sleep(2)

    language = request.language.lower()

    if language in ["cpp", "c++"]:
        result = analyze_cpp_code(request.code)

    elif language in ["javascript", "js"]:
        result = analyze_javascript_code(request.code)

    elif language == "java":
        result = analyze_java_code(request.code)

    elif language == "go":
        result = analyze_go_code(request.code)

    else:
        result = agent.process(request.code)

    if result.get("status") == "success" and not result.get("llm_analysis"):
        try:
            result["llm_analysis"] = get_llm_analysis(
                request.code,
                result
            )
        except Exception as e:
            print("LLM Error:", e)
            result["llm_analysis"] = "LLM analizi şu anda çalışmıyor."

    return result
@app.post("/fix")
def fix(request: CodeRequest):

    print(
        f"Fix endpoint çağrıldı | Dil: {request.language} | Kod uzunluğu: {len(request.code)} karakter"
    )

    if request.language in ["cpp", "c++"]:

        lines = request.code.splitlines()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                fixed_lines.append(line)
                continue

            if stripped.startswith("#") or stripped.startswith("//"):
                fixed_lines.append(line)
                continue

            if (
                stripped.endswith(";")
                or stripped.endswith("{")
                or stripped.endswith("}")
                or stripped.endswith(":")
            ):
                fixed_lines.append(line)
                continue

            control_keywords = ("if", "for", "while", "switch", "else", "do")

            if stripped.startswith(control_keywords):
                fixed_lines.append(line)
                continue

            if stripped.startswith(("int main", "void main", "int ", "void ", "float ", "double ", "char ", "bool ")):
                if "(" in stripped and ")" in stripped:
                    fixed_lines.append(line)
                    continue

            fixed_lines.append(line + ";")

        fixed_code = "\n".join(fixed_lines)

        open_braces = fixed_code.count("{")
        close_braces = fixed_code.count("}")

        while close_braces < open_braces:
            fixed_code += "\n}"
            close_braces += 1

        return {
            "status": "fixed",
            "language": "cpp",
            "fixed_code": fixed_code,
            "message": "C++ kodundaki eksik noktalı virgül ve süslü parantez hataları otomatik düzeltildi."
        }

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
