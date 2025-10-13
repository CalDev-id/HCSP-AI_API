import os
from groq import Groq
from dotenv import load_dotenv


class GroqRunTime:
    def __init__(self):
        # Load .env dan ambil API key dari environment
        load_dotenv()
        self.api_key = os.getenv("GROQ_KEY")

        # Inisialisasi client Groq
        self.client = Groq(
            api_key=self.api_key,
        )

    def generate_response(self, system_prompt, user_prompt):
        responses = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            # model="meta-llama/llama-4-scout-17b-16e-instruct"
            model="llama-3.3-70b-versatile"
            # model="llama-3.1-8b-instant"
        )
        return responses.choices[0].message.content.strip()
