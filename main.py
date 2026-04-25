from fastapi import FastAPI
from pydantic import BaseModel
import ast

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.get("/")
def home():
    return {"message": "Backend çalışıyor 🚀"}

@app.post("/analyze")
def analyze(request: CodeRequest):
    code = request.code

    try:
        tree = ast.parse(code)

        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        loop_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))])
        if_count = len([node for node in ast.walk(tree) if isinstance(node, ast.If)])

        complexity_score = len(functions) + (loop_count * 2) + if_count

        if complexity_score <= 3:
            complexity_level = "low"
        elif complexity_score <= 7:
            complexity_level = "medium"
        else:
            complexity_level = "high"
        
        explanation = f"Bu kodda {len(functions)} fonksiyon, {loop_count} döngü ve {if_count} koşul bulunmaktadır. Kod {complexity_level} seviyede karmaşıklığa sahiptir."

        return {
            "status": "success",
            "functions": functions,
            "loop_count": loop_count,
            "if_count": if_count,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
            "explanation": explanation
        }

    except SyntaxError as e:
        return {
            "status": "error",
            "message": f"Syntax error: {e}"
        }