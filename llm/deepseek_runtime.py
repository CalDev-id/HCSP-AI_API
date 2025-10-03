import os
import requests
import json
import re


class DeepseekRunTime:
    def __init__(self):
        # baca api_key dari file
        with open("config/secrets/apilogy_LLM.txt", "r") as f:
            os.environ["APILOGY_API_KEY"] = f.read().strip()

        self.api_key = os.environ.get("APILOGY_API_KEY")
        self.url = "https://telkom-ai-dag.api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions"

    def generate_response(self, system_prompt: str, user_prompt: str):
        payload = {
            "model": "telkom-ai-reasoning",
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
                response = clean_response(response)
                return response
            else:
                print("Tidak ada respons dari AI.")
                return ""

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return ""




def clean_response(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
