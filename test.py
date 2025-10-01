# import requests
# import json

# url = "https://telkom-ai-dag.api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions"
# api_key = "ZRfH4nfAPQOxHAA4knKT0POlo1b24ZzT"

# payload = json.dumps({
#   "messages": [
#     {
#       "role": "system",
#       "content": "PLEASE ANSWER IN BAHASA INDONESIA"
#     },
#     {
#       "role": "user",
#       "content": "lebih pintar mana Qwen 2.5 atau deepseek"
#     }
#   ],
#   "max_tokens": 2000,
#   "temperature": 0.2,
#   "stream": False
# })

# headers = {
#   'Accept': 'application/json',
#   'Content-Type': 'application/json',
#   'x-api-key': api_key
# }

# response = requests.post(url, headers=headers, data=payload)

# print(response.status_code)
# print(response.text)


import re

def fix_word_case(text: str) -> str:
    def repl(match):
        word = match.group(0)

        if word.islower() or word.isupper() or word.istitle():
            return word
        if re.match(r'^[A-Z]?[a-z]+(?:[A-Z][a-z]+)+$', word):
            return word  

        return word.upper()

    return re.sub(r"\b\w+\b", repl, text)


text = "Mengembangkan solusi EsS dengan DevSecOps"
fixed_text = fix_word_case(text)
print(fixed_text)
