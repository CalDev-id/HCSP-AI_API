from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ms_agent(nama_posisi: str, retrieve_data: List[dict]):
    apilogy_run = ApilogyRunTime()
    
    if not retrieve_data:
      context_text = "Tidak ada konteks pasal relevan."
    else:
      context_parts = []
      for record in retrieve_data:
          jobId = record.get("jobId", "")
          nama_posisi = record.get("nama_posisi", "")
          mission_statement = record.get("mission_statement", "")
          job_responsibilities = record.get("job_responsibilities", "")
          job_performance = record.get("job_performance", "")
          job_authorities = record.get("job_authorities", "")
          context_parts.append(f"Job ID: {jobId}\nNama Posisi: {nama_posisi}\nMission Statement: {mission_statement}\nJob Responsibilities: {job_responsibilities}\nJob Performance: {job_performance}\nJob Authorities: {job_authorities}\n")
        
      context_text = "\n\n".join(context_parts)

    user_prompt = f"""
sekarang, buatkan mission statement untuk posisi berikut : Nama Posisi :{nama_posisi} Mission Statement hanya berupa teks narasi langsung sebutkan misinya tanpa ada kata pengantarnya, tanpa penanda seperti (-/*), dan tidak dibold !
    """

    system_prompt = f"""
Peranmu: Kamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi. Tugas Utama: 1. Pahami informasi mengenai posisi yang diberikan. 2. Cara berpikir kamu: - Reasoning: - Pahami posisi dan nama fungsi posisi itu. - Act: - Buat mission statement dengan rumus: Mission Statement = “Melakukan pengelolaan fungsi ” + (nama fungsi) + “ untuk mendukung pencapaian performansi” 3. Output atau jawaban anda langsung MS nya tanpa ada kata pengantar IKUTI Contoh BERIKUT : Input: SO DIGITAL PLATFORM STRATEGY Reasoning: → pakai rumus : Mission Statement = “Melakukan pengelolaan fungsi ” + (nama fungsi) + “ untuk mendukung pencapaian performansi” Output (Mission Statement): Melakukan pengelolaan fungsi Digital Platform Strategy untuk mendukung pencapaian performansi.

"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)
    return response