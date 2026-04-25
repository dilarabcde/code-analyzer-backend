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

        functions = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]

        loop_count = len([
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.For, ast.While))
        ])

        if_count = len([
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.If)
        ])

        imports = []
        dangerous_calls = []
        risk_warnings = []
        risk_score = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                function_name = node.func.id

                if function_name in ["eval", "exec"]:
                    dangerous_calls.append(function_name)
                    risk_score += 5
                    risk_warnings.append(
                        f"{function_name} kullanımı güvenlik riski oluşturabilir."
                    )

            elif isinstance(node, ast.While):
                risk_score += 2
                risk_warnings.append(
                    "while döngüsü dikkatli kullanılmalıdır; sonsuz döngü riski olabilir."
                )

        if "os" in imports:
            risk_score += 2
            risk_warnings.append(
                "os modülü sistem seviyesinde işlemler yapabileceği için dikkatli kullanılmalıdır."
            )

        if "subprocess" in imports:
            risk_score += 4
            risk_warnings.append(
                "subprocess modülü dış komut çalıştırabileceği için yüksek riskli olabilir."
            )

        if risk_score == 0:
            risk_level = "safe"
        elif risk_score <= 4:
            risk_level = "low"
        elif risk_score <= 7:
            risk_level = "medium"
        else:
            risk_level = "high"

        complexity_score = len(functions) + (loop_count * 2) + if_count

        if complexity_score <= 3:
            complexity_level = "low"
        elif complexity_score <= 7:
            complexity_level = "medium"
        else:
            complexity_level = "high"

        explanation = (
            f"Bu kodda {len(functions)} fonksiyon, "
            f"{loop_count} döngü ve {if_count} koşul bulunmaktadır."
        )

        rule_based_analysis = ""
        
        suggestions = []

        if "eval" in dangerous_calls:
            suggestions.append("eval yerine ast.literal_eval kullanabilirsin.")

        if "exec" in dangerous_calls:
            suggestions.append("exec kullanımı tehlikelidir, alternatif yöntemler tercih edilmelidir.")

        if "os" in imports:
            suggestions.append("os modülü kullanırken kullanıcı girdilerini doğrula.")

        if "subprocess" in imports:
            suggestions.append("subprocess kullanırken dış komutları sanitize et.")

        if loop_count > 0:
            suggestions.append("Döngülerde çıkış koşullarının doğru tanımlandığından emin ol.")

        if complexity_level == "high":
            suggestions.append("Kod karmaşıklığını azaltmak için fonksiyonları bölmeyi düşünebilirsin.")
            
        if risk_level == "high":
            rule_based_analysis += "Kod yüksek güvenlik riski içermektedir. "
        elif risk_level == "medium":
            rule_based_analysis += "Kod orta seviyede güvenlik riski barındırmaktadır. "
        elif risk_level == "low":
            rule_based_analysis += "Kod düşük seviyede güvenlik riski barındırmaktadır. "
        else:
            rule_based_analysis += "Kod güvenlik açısından temel seviyede güvenli görünmektedir. "

        if complexity_level == "high":
            rule_based_analysis += "Kod karmaşıklığı yüksektir; okunabilirlik ve bakım zorlaşabilir. "
        elif complexity_level == "medium":
            rule_based_analysis += "Kod orta seviyede karmaşıklığa sahiptir. "
        else:
            rule_based_analysis += "Kod basit ve anlaşılır yapıdadır. "

        if dangerous_calls:
            rule_based_analysis += (
                f"Riskli fonksiyon kullanımı tespit edildi: {', '.join(dangerous_calls)}. "
            )

        if "os" in imports:
            rule_based_analysis += "Kod işletim sistemi seviyesinde işlem yapabilecek os modülünü kullanıyor. "

        if "subprocess" in imports:
            rule_based_analysis += "Kod dış komut çalıştırmaya izin veren subprocess modülünü kullanıyor. "

        if not risk_warnings:
            risk_warnings.append("Belirgin bir güvenlik riski tespit edilmedi.")

        return {
            "status": "success",
            "functions": functions,
            "loop_count": loop_count,
            "if_count": if_count,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
            "explanation": explanation,
            "imports": imports,
            "dangerous_calls": dangerous_calls,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_warnings": risk_warnings,
            "analysis": rule_based_analysis,
            "suggestions": suggestions
        }

    except SyntaxError as e:
        return {
            "status": "error",
            "message": f"Syntax error: {e}"
        }