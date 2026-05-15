import requests


def get_llm_analysis(code: str, analysis_result: dict):
    prompt = f"""
Sen kıdemli bir yazılım mühendisi gibi davran.

Aşağıdaki Python kodunu ve statik analiz sonucunu incele.
Kullanıcıya Türkçe, kısa ama teknik bir açıklama üret.

Şunları açıkla:
1. Kod genel olarak ne yapıyor?
2. Riskli veya karmaşık yerler var mı?
3. Geliştiriciye 3 iyileştirme önerisi ver.

KOD:
{code[:4000]}

STATİK ANALİZ:
{analysis_result}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return "LLM servisi cevap veremedi. Ollama çalışıyor mu kontrol et."

        data = response.json()
        return data.get("response", "LLM analizi alınamadı.")

    except Exception as e:
        return f"LLM bağlantı hatası: {str(e)}"