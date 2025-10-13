import requests
import json
import os
from dotenv import load_dotenv

# Load .env dan ambil API key
load_dotenv()
API_KEY = os.getenv("APILOGY_LMM_KEY")

URL = "https://telkom-ai-dag.api.apilogy.id/Text_Embedding/0.0.1/v1/embeddings"

def get_embedding(text: str):
    payload = json.dumps({
        "input": [text]
    })

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
    }

    response = requests.post(URL, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Embedding API error {response.status_code}: {response.text}")

    data = response.json()
    return data["data"][0]["embedding"]
