import os
import requests
import json
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

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=100)
            response.raise_for_status()
            response = response.json()

            if response and "choices" in response:
                response = response["choices"][0]["message"]["content"].strip()
                return response
            else:
                print("Tidak ada respons dari AI.")
                return ""

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return ""
