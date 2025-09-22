import os
import requests
import json

class ApilogyRunTime:
    def __init__(self):
        # baca api_key dari file
        with open("config/secrets/apilogy_LLM.txt", "r") as f:
            os.environ["APILOGY_API_KEY"] = f.read().strip()

        self.api_key = os.environ.get("APILOGY_API_KEY")
        self.url = "https://telkom-ai-dag.api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions"

    def generate_response(self, system_prompt: str, user_prompt: str):
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 10000,
            "temperature": 0.0,
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
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

# my_runtime = ApilogyRunTime()

# if __name__ == "__main__":
#     system_prompt = "jawab dengan bahasa indonesia"
#     user_prompt = "halo ayang"
#     response = my_runtime.generate_response(system_prompt, user_prompt)
#     print(response)