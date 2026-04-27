import ast


def get_risk_level(score: int) -> str:
    if score == 0:
        return "safe"
    elif score <= 4:
        return "low"
    elif score <= 7:
        return "medium"
    return "high"


def get_complexity_level(score: int) -> str:
    if score <= 3:
        return "low"
    elif score <= 7:
        return "medium"
    return "high"


def analyze_code(code: str):
    if not code.strip():
        return {
            "status": "error",
            "message": "Kod alanı boş olamaz.",
            "suggestion": "Lütfen analiz edilecek Python kodunu gir."
        }

    try:
        tree = ast.parse(code)

        functions = []
        imports = []
        dangerous_calls = []
        risk_warnings = []
        suggestions = []

        loop_count = 0
        if_count = 0
        risk_score = 0
        max_depth = 0

        risky_imports = {
            "os": 2,
            "subprocess": 4,
            "pickle": 4,
            "socket": 3,
            "shutil": 3
        }

        risky_functions = {
            "eval": 5,
            "exec": 5,
            "compile": 4,
            "open": 2,
            "input": 1
        }

        def calculate_depth(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            for child in ast.iter_child_nodes(node):
                calculate_depth(child, depth + 1)

        calculate_depth(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

            elif isinstance(node, (ast.For, ast.While)):
                loop_count += 1

                if isinstance(node, ast.While):
                    risk_score += 2
                    risk_warnings.append(
                        "while döngüsü dikkatli kullanılmalıdır; sonsuz döngü riski olabilir."
                    )

            elif isinstance(node, ast.If):
                if_count += 1

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                function_name = node.func.id

                if function_name in risky_functions:
                    dangerous_calls.append(function_name)
                    risk_score += risky_functions[function_name]
                    risk_warnings.append(
                        f"{function_name} kullanımı güvenlik veya kontrol riski oluşturabilir."
                    )

        for module_name in imports:
            root_module = module_name.split(".")[0]

            if root_module in risky_imports:
                risk_score += risky_imports[root_module]
                risk_warnings.append(
                    f"{root_module} modülü sistem, dosya veya dış işlem riski oluşturabilir."
                )

        line_count = len(code.splitlines())
        function_count = len(functions)

        complexity_score = (
            function_count
            + (loop_count * 2)
            + if_count
            + max(0, max_depth - 8)
        )

        complexity_level = get_complexity_level(complexity_score)
        risk_level = get_risk_level(risk_score)

        explanation = (
            f"Bu kodda {function_count} fonksiyon, "
            f"{loop_count} döngü, {if_count} koşul ve "
            f"{line_count} satır bulunmaktadır."
        )

        if not risk_warnings:
            risk_warnings.append("Belirgin bir güvenlik riski tespit edilmedi.")

        if "eval" in dangerous_calls:
            suggestions.append("eval yerine ast.literal_eval veya güvenli parsing yöntemleri kullanılabilir.")

        if "exec" in dangerous_calls:
            suggestions.append("exec kullanımından kaçınılmalı; çalıştırılacak işlemler açık fonksiyonlara ayrılmalıdır.")

        if "compile" in dangerous_calls:
            suggestions.append("compile kullanımı sınırlandırılmalı ve kullanıcı girdisiyle birlikte kullanılmamalıdır.")

        if "open" in dangerous_calls:
            suggestions.append("Dosya işlemlerinde dosya yolu doğrulaması yapılmalıdır.")

        if "input" in dangerous_calls:
            suggestions.append("Kullanıcı girdileri doğrulanmadan işleme alınmamalıdır.")

        if "os" in imports:
            suggestions.append("os modülü kullanılırken kullanıcı girdileri mutlaka doğrulanmalıdır.")

        if "subprocess" in imports:
            suggestions.append("subprocess kullanırken komutlar sanitize edilmeli ve shell=True kullanımından kaçınılmalıdır.")

        if "pickle" in imports:
            suggestions.append("pickle güvenilmeyen verilerle kullanılmamalıdır; JSON gibi daha güvenli formatlar tercih edilebilir.")

        if loop_count > 0:
            suggestions.append("Döngülerde çıkış koşullarının doğru tanımlandığından emin olunmalıdır.")

        if complexity_level == "high":
            suggestions.append("Karmaşıklığı azaltmak için kod daha küçük fonksiyonlara bölünebilir.")

        if line_count > 100:
            suggestions.append("Kod dosyası uzun görünüyor; modüllere ayırmak okunabilirliği artırabilir.")

        if not suggestions:
            suggestions.append("Kod genel olarak sade görünüyor; okunabilirliği koruyarak geliştirmeye devam edilebilir.")

        summary = ""

        if risk_level == "high":
            summary += "Kod yüksek güvenlik riski içermektedir. "
        elif risk_level == "medium":
            summary += "Kod orta seviyede güvenlik riski barındırmaktadır. "
        elif risk_level == "low":
            summary += "Kod düşük seviyede güvenlik riski barındırmaktadır. "
        else:
            summary += "Kod güvenlik açısından temel seviyede güvenli görünmektedir. "

        if complexity_level == "high":
            summary += "Kod karmaşıklığı yüksektir; okunabilirlik ve bakım zorlaşabilir."
        elif complexity_level == "medium":
            summary += "Kod orta seviyede karmaşıklığa sahiptir."
        else:
            summary += "Kod basit ve anlaşılır yapıdadır."

        return {
            "status": "success",
            "analysis": {
                "functions": functions,
                "function_count": function_count,
                "loops": loop_count,
                "conditions": if_count,
                "line_count": line_count,
                "max_depth": max_depth,
                "complexity": {
                    "score": complexity_score,
                    "level": complexity_level
                }
            },
            "security": {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "imports": imports,
                "dangerous_calls": dangerous_calls,
                "warnings": risk_warnings
            },
            "explanation": explanation,
            "summary": summary,
            "suggestions": suggestions
        }

    except SyntaxError as e:
        return {
            "status": "error",
            "message": "Kodda syntax hatası var.",
            "detail": str(e),
            "suggestion": "Parantezleri, girintileri ve eksik ':' karakterlerini kontrol et."
        }