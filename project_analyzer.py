import ast
from analyzer import analyze_code
from llm_service import get_llm_analysis


# llm hata verirse tüm proje analizinin çökmesini engelleyecel
def safe_llm_analysis(code, analysis):
    try:
        return get_llm_analysis(code, analysis)
    except Exception as e:
        print("LLM project analysis error:", e)
        return "LLM analizi şu anda alınamadı."


# dosyadan fonksiyon, class, import ve api bilgilerini çıkarıyoruz
def extract_code_details(code):
    details = {
        "functions": [],
        "classes": [],
        "imports": [],
        "api_routes": [],
        "calls": []
    }

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                details["functions"].append(node.name)

            elif isinstance(node, ast.ClassDef):
                details["classes"].append(node.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    details["imports"].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    details["imports"].append(node.module)

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    details["calls"].append(node.func.attr)

                    # fastapi route tanımlarını yakalamaya çalışıyo
                    if node.func.attr in ["get", "post", "put", "delete", "patch"]:
                        if node.args and isinstance(node.args[0], ast.Constant):
                            details["api_routes"].append(
                                f"{node.func.attr.upper()} {node.args[0].value}"
                            )

                elif isinstance(node.func, ast.Name):
                    details["calls"].append(node.func.id)

    except Exception:
        pass

    return details


# dosyanın ne işe yaradığını kod yapısından tahmin ediyoruz
def generate_file_purpose(filename, details):
    functions = details["functions"]
    classes = details["classes"]
    imports = details["imports"]
    api_routes = details["api_routes"]
    calls = details["calls"]

    sentences = []

    if api_routes:
        sentences.append(
            f"Bu dosya API katmanında görev alıyor. Tanımlanan endpointler: {', '.join(api_routes)}."
        )

    if classes:
        sentences.append(
            f"Dosyada şu sınıflar bulunuyor: {', '.join(classes)}."
        )

    if functions:
        sentences.append(
            f"Dosyanın ana fonksiyonları: {', '.join(functions[:6])}."
        )

    if "fastapi" in imports or "fastapi.middleware.cors" in imports:
        sentences.append(
            "FastAPI kullanıldığı için backend servisinin istek/cevap akışını yönetiyor olabilir."
        )

    if "agent" in imports or "CodeAnalysisAgent" in classes:
        sentences.append(
            "Agent yapısıyla bağlantılı olduğu için analiz sürecini yöneten karar katmanı ile ilişkilidir."
        )

    if "analyze_code" in calls or "ast" in imports:
        sentences.append(
            "Kod AST veya analiz fonksiyonlarıyla işlendiği için syntax, karmaşıklık ve güvenlik analizi yapıyor olabilir."
        )

    if "UploadFile" in calls or "File" in calls:
        sentences.append(
            "Dosya yükleme işlemleri içerdiği için proje veya çoklu dosya analiziyle ilişkilidir."
        )

    if "fix_code" in calls:
        sentences.append(
            "Kod düzeltme fonksiyonu çağırdığı için otomatik hata düzeltme akışında görev alıyor."
        )

    if not sentences:
        sentences.append("Bu dosyanın görevi kod yapısından sınırlı şekilde çıkarılabildi.")

    return " ".join(sentences)


# proje içindeki dosyaların birbirine bağımlılığını çıkarıyoruz
def build_dependency_graph(file_details):
    graph = {}

    project_modules = {
        filename.replace(".py", "")
        for filename in file_details.keys()
        if filename.endswith(".py")
    }

    for filename, details in file_details.items():
        dependencies = []

        for imported_module in details["imports"]:
            root_module = imported_module.split(".")[0]

            if root_module in project_modules:
                dependencies.append(f"{root_module}.py")

        graph[filename] = sorted(list(set(dependencies)))

    return graph


# tüm proje dosyalarını tek tek analiz eden ana fonksiyon
def analyze_project(files):
    file_reports = []
    file_details = {}
    total_lines = 0
    total_functions = 0
    risky_files = []

    most_complex_file = None
    highest_complexity_score = -1

    # en karmaşık dosyayı bulmak için seviyelere basit skor verdim
    complexity_scores = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    for file in files:
        filename = file["filename"]
        code = file["content"]

        details = extract_code_details(code)
        file_details[filename] = details

        analysis = analyze_code(code)

        if analysis.get("status") == "success":
            line_count = analysis["analysis"]["line_count"]
            function_count = analysis["analysis"]["function_count"]
            risk_level = analysis["security"]["risk_level"]
            complexity_level = analysis["analysis"]["complexity"]["level"]

            total_lines += line_count
            total_functions += function_count

            if risk_level in ["medium", "high"]:
                risky_files.append(filename)

            current_complexity_score = complexity_scores.get(complexity_level, 0)

            if current_complexity_score > highest_complexity_score:
                highest_complexity_score = current_complexity_score
                most_complex_file = {
                    "filename": filename,
                    "complexity": complexity_level,
                    "line_count": line_count,
                    "function_count": function_count
                }

            file_reports.append({
                "filename": filename,
                "status": "success",
                "line_count": line_count,
                "function_count": function_count,
                "risk_level": risk_level,
                "complexity": complexity_level,
                "summary": analysis["summary"],
                "suggestions": analysis["suggestions"],
                "purpose": generate_file_purpose(filename, details),
                "functions": details["functions"],
                "classes": details["classes"],
                "imports": details["imports"],
                "api_routes": details["api_routes"],
                # llm hata verse bile proje analizi devam etsin
                "llm_analysis": safe_llm_analysis(code, analysis),
            })

        else:
            file_reports.append({
                "filename": filename,
                "status": "error",
                "message": analysis.get("message"),
                "suggestion": analysis.get("suggestion"),
                "error_line": analysis.get("error_line"),
                "purpose": generate_file_purpose(filename, details),
                "functions": details["functions"],
                "classes": details["classes"],
                "imports": details["imports"],
                "api_routes": details["api_routes"]
            })

    dependency_graph = build_dependency_graph(file_details)

    project_summary = (
        f"Bu projede {len(file_reports)} dosya analiz edildi. "
        f"Toplam {total_lines} satır kod ve {total_functions} fonksiyon tespit edildi. "
    )

    if risky_files:
        project_summary += f"Riskli görünen dosyalar: {', '.join(risky_files)}."
    else:
        project_summary += "Belirgin yüksek riskli dosya tespit edilmedi."

    return {
        "status": "success",
        "project_summary": project_summary,
        "file_reports": file_reports,
        "most_complex_file": most_complex_file,
        "dependency_graph": dependency_graph
    }