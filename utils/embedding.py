import requests
import json

API_KEY = "dDCnOxb8sWENQov9uZzCv6Of4YLxnvHt"
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
    # asumsi struktur respons: {"data": [{"embedding": [..list of floats..]}]}
    return data["data"][0]["embedding"]
