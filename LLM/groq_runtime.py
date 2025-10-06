import os
from groq import Groq

class GroqRunTime:
    def __init__(self):
        # Baca API key dari file dan simpan ke environment
        with open("config/secrets/api_key.txt", "r") as txt_r:
            os.environ["GROQ_API_KEY"] = txt_r.readline().strip()
        
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def generate_response(self, system_prompt, user_prompt):
        # Panggil model Groq
        responses = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile"
            # model alternatif:
            # model="llama-3.1-8b-instant"
        )

        # ✅ Hanya return content teks (tanpa metadata)
        return responses.choices[0].message.content.strip()
