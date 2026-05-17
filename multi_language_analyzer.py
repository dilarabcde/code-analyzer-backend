import re


def check_cpp_syntax(code: str):
    if not code.strip():
        return {
            "has_error": True,
            "error_line": 1,
            "message": "Kod alanı boş olamaz."
        }

    open_braces = code.count("{")
    close_braces = code.count("}")

    if open_braces != close_braces:
        return {
            "has_error": True,
            "error_line": 1,
            "message": "C++ syntax hatası: Süslü parantez sayıları eşleşmiyor."
        }

    open_parentheses = code.count("(")
    close_parentheses = code.count(")")

    if open_parentheses != close_parentheses:
        return {
            "has_error": True,
            "error_line": 1,
            "message": "C++ syntax hatası: Parantez sayıları eşleşmiyor."
        }

    if "main(" not in code:
        return {
            "has_error": True,
            "error_line": 1,
            "message": "C++ syntax hatası: main fonksiyonu bulunamadı."
        }

    lines = code.splitlines()

    for index, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        if stripped.endswith("{") or stripped.endswith("}") or stripped.endswith(":"):
            continue

        if stripped.startswith("//"):
            continue

        control_keywords = ("if", "for", "while", "switch", "else", "do")

        if stripped.startswith(control_keywords):
            continue

        if stripped.endswith(";"):
            continue

        if re.match(r"^(int|void|float|double|char|bool|string|auto)\s+\w+\s*\(.*\)$", stripped):
            continue

        return {
            "has_error": True,
            "error_line": index,
            "message": f"C++ syntax hatası: {index}. satırda noktalı virgül veya geçerli yapı eksik olabilir."
        }

    return {
        "has_error": False,
        "error_line": None,
        "message": "C++ syntax valid."
    }


def analyze_cpp_code(code: str):
    syntax_result = check_cpp_syntax(code)

    if syntax_result["has_error"]:
        return {
            "status": "error",
            "language": "cpp",
            "message": syntax_result["message"],
            "error_line": syntax_result["error_line"],
            "suggestion": "C++ syntax hatasını düzeltip tekrar analiz edin."
        }

    lines = code.splitlines()
    line_count = len(lines)

    risk_patterns = {
        "system(": "system() kullanımı komut çalıştırma riski oluşturabilir.",
        "strcpy(": "strcpy() buffer overflow riski oluşturabilir.",
        "gets(": "gets() güvenli değildir, buffer overflow riski vardır.",
        "malloc(": "malloc kullanımı manuel bellek yönetimi gerektirir.",
        "free(": "free kullanımı bellek yönetimi hatalarına yol açabilir.",
        "new ": "new kullanımı memory leak riski oluşturabilir.",
        "delete ": "delete kullanımı dikkatli yönetilmezse hata oluşturabilir.",
        "char *": "raw char pointer kullanımı güvenlik riski oluşturabilir."
    }

    risks = []

    for index, line in enumerate(lines, start=1):
        for pattern, message in risk_patterns.items():
            if pattern in line:
                risks.append({
                    "line": index,
                    "pattern": pattern,
                    "message": message
                })

    function_matches = re.findall(
        r"\b(int|void|float|double|char|bool|string|auto)\s+\w+\s*\([^)]*\)\s*\{",
        code
    )

    function_count = len(function_matches)

    loop_count = len(re.findall(r"\b(for|while)\b", code))
    condition_count = len(re.findall(r"\b(if|switch)\b", code))

    complexity_score = loop_count + condition_count + len(risks)

    if complexity_score >= 8:
        complexity_level = "high"
    elif complexity_score >= 4:
        complexity_level = "medium"
    else:
        complexity_level = "low"

    if len(risks) >= 3:
        risk_level = "high"
    elif len(risks) >= 1:
        risk_level = "medium"
    else:
        risk_level = "safe"

    return {
        "status": "success",
        "language": "cpp",
        "line_count": line_count,
        "function_count": function_count,
        "risk_level": risk_level,
        "complexity": complexity_level,
        "security": {
            "risk_level": risk_level,
            "risks": risks
        },
        "analysis": {
            "complexity": {
                "score": complexity_score,
                "level": complexity_level
            }
        },
        "summary": f"C++ kodu analiz edildi. {line_count} satır, {function_count} fonksiyon ve {len(risks)} riskli kullanım tespit edildi.",
        "suggestions": [
            "Raw pointer kullanımını mümkün olduğunca azaltın.",
            "strcpy, gets, system gibi güvenli olmayan fonksiyonlardan kaçının.",
            "Bellek yönetimi için modern C++ yapıları kullanın.",
            "std::string, std::vector ve smart pointer kullanımı tercih edilebilir."
        ]
    }
def analyze_javascript_code(code: str):

    if not code.strip():
        return {
            "status": "error",
            "message": "Kod alanı boş olamaz."
        }

    risks = []

    risk_patterns = {
        "eval(": "eval kullanımı güvenlik riski oluşturabilir.",
        "innerHTML": "innerHTML XSS riski oluşturabilir.",
        "document.write": "document.write güvenli değildir.",
        "localStorage": "Hassas veri localStorage içinde tutulmamalıdır."
    }

    lines = code.splitlines()

    for index, line in enumerate(lines, start=1):
        for pattern, message in risk_patterns.items():
            if pattern in line:
                risks.append({
                    "line": index,
                    "pattern": pattern,
                    "message": message
                })

    syntax_error = None

    open_braces = code.count("{")
    close_braces = code.count("}")

    if open_braces != close_braces:
        syntax_error = "Süslü parantez sayıları eşleşmiyor."

    return {
        "status": "error" if syntax_error else "success",
        "language": "javascript",
        "message": syntax_error if syntax_error else "JavaScript kodu analiz edildi.",
        "security": {
            "risk_level": "high" if len(risks) >= 3 else "medium" if risks else "safe",
            "risks": risks
        },
        "summary": "JavaScript kodu analiz edildi."
    }