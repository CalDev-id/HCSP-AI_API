from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ms_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict]):
    apilogy_run = ApilogyRunTime()
    
    if not retrieve_data:
      context_text = "Tidak ada konteks pasal relevan."
    else:
      context_parts = []
      for record in retrieve_data:
          job_responsibilities = record.get("job_responsibilities", "")
          context_parts.append(f"Job Responsibilities: {job_responsibilities}\n\n")
        
      context_text = "\n\n".join(context_parts)


    user_prompt = f"""
sekarang, buatkan mission statement untuk posisi berikut :\n\nNama Posisi : {nama_posisi} \n\nMission Statement hanya berupa teks narasi langsung sebutkan misinya tanpa ada kata pengantarnya, tanpa penanda seperti (-/*), dan tidak dibold !
    """

    system_prompt = f"""
Peranmu:\nKamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi.\n\nTugas Utama:\n1. Pahami informasi mengenai posisi yang diberikan.\n\n2. Cara berpikir kamu:\n   - Reasoning:\n     - Pahami posisi dan nama fungsi posisi itu.\n   - Act:\n - Buat mission statement dengan rumus:\n Mission Statement = “Melakukan pengelolaan fungsi ” + (nama fungsi) + “ untuk mendukung pencapaian performansi”\n\n3. Output atau jawaban anda langsung MS nya tanpa ada kata pengantar\n IKUTI Contoh BERIKUT :\n\nInput:\n SO DIGITAL PLATFORM STRATEGY \n\nReasoning:\n→ pakai rumus : Mission Statement = “Melakukan pengelolaan fungsi ” + (nama fungsi) + “ untuk mendukung pencapaian performansi”\n\nOutput (Mission Statement):\nMelakukan pengelolaan fungsi Digital Platform Strategy untuk mendukung pencapaian performansi.
"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        mission_statement = response["choices"][0]["message"]["content"].strip()
        return mission_statement
    else:
        print("Tidak ada respons dari AI.")
        return ""