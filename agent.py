from analyzer import analyze_code
from llm_service import get_llm_analysis


class CodeAnalysisAgent: # ana analiz akışını yöneten agent yapısı
    def __init__(self):
        self.name = "Code Analysis Agent"

    def process(self, code: str):
        if not code.strip(): # boş kod gönderilirse gereksiz analiz başlatma
            return {
                "status": "error",
                "message": "Kod alanı boş olamaz.",
                "suggestion": "Lütfen analiz edilecek Python kodunu gir."
            }

        result = analyze_code(code) # temel syntax ve güvenlik analizleri

        # Syntax error varsa LLM'e gitme
        if result.get("status") == "error": # syntax hatası varsa llm analizine geçmeyecek
            result["agent_name"] = self.name
            result["agent_status"] = "Agent syntax hatası nedeniyle LLM analizini çalıştırmadı."
            return result

        llm_response = get_llm_analysis(code, result) # llm tarafında kodun daha detaylı yorumu oluşturuluyor

        result["llm_analysis"] = llm_response
        result["agent_name"] = self.name # frontend tarafında hangi agentin çalıştığını göstermek için
        result["agent_status"] = "Agent analiz sürecini başarıyla tamamladı."

        return result