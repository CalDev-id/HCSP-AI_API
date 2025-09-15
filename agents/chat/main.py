from llm.groq_runtime import GroqRunTime

def chat_agent(query: str):
    groq_run = GroqRunTime()
    system_prompt = (
        "Anda adalah asisten pengambil nama makanan dari kalimat. "
        "Tolong ubah atau ringkas kalimat pengguna agar lebih jelas untuk pencarian makanan. "
        "Hanya respon dengan ringkasan makanan pengguna."
    )
    response = groq_run.generate_response(system_prompt, query)
    print(response.choices[0].message.content)
    return response.choices[0].message.content