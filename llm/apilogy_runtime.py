import os
import requests
import json
import time
from dotenv import load_dotenv


class ApilogyRunTime:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("APILOGY_LLM_KEY")
        self.url = "https://telkom-ai-dag.api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions"

    def generate_response(self, system_prompt: str, user_prompt: str):
        payload = {
            # "model": "telkom-ai-reasoning",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 10000,
            "temperature": 0.1,
            "stream": False
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

        max_retries = 3
        delay_seconds = 5

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(self.url, headers=headers, json=payload, timeout=100)
                
                # Cek status code
                if response.status_code == 200:
                    data = response.json()
                    if data and "choices" in data:
                        content = data["choices"][0]["message"]["content"].strip()
                        return content
                    else:
                        print("⚠️ Tidak ada respons dari AI.")
                        return ""
                else:
                    print(f"⚠️ Request gagal (status {response.status_code}). Percobaan ke-{attempt}/3.")
            
            except requests.exceptions.RequestException as e:
                print(f"❌ Error saat request (percobaan ke-{attempt}/3): {e}")

            if attempt < max_retries:
                print(f"⏳ Menunggu {delay_seconds} detik sebelum mencoba lagi...")
                time.sleep(delay_seconds)

        print("❌ Gagal mendapatkan respons setelah 3 percobaan.")
        return ""
