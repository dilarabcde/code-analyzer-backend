import requests


def get_llm_analysis(code, static_result):
    prompt = f"""
Sen uzman bir AI Code Review Agent'sın.

Aşağıdaki Python kodunu analiz et.

Kod:
{code}

Statik analiz sonucu:
{static_result}

Kısa ve Türkçe cevap ver:
1. Kod ne yapıyor?
2. Güvenlik riski var mı?
3. Nasıl iyileştirilebilir?
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    except Exception as e:
        return f"Lokal LLM analizi alınamadı: {str(e)}"