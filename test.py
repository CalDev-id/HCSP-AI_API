import requests
import json

url = "https://telkom-ai-dag.api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions"
api_key = "ZRfH4nfAPQOxHAA4knKT0POlo1b24ZzT"

payload = json.dumps({
  "messages": [
    {
      "role": "system",
      "content": "PLEASE ANSWER IN BAHASA INDONESIA"
    },
    {
      "role": "user",
      "content": "lebih pintar mana Qwen 2.5 atau deepseek"
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.2,
  "stream": False
})

headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'x-api-key': api_key
}

response = requests.post(url, headers=headers, data=payload)

print(response.status_code)
print(response.text)
