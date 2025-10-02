from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ms_agent(nama_posisi: str):
    apilogy_run = ApilogyRunTime()

    user_prompt = f"""
sekarang, buatkan mission statement untuk posisi berikut. WAJIB IKUTI CONTOH, HANYA AMBIL NAMA FUNGSI BUKAN PREFIX JABATANNYA. => Nama Posisi :{nama_posisi} Mission Statement hanya berupa teks narasi 1 kalimat serta langsung sebutkan misinya tanpa ada kata pengantarnya, tanpa penanda seperti (-/*), dan tidak dibold !    
"""

    system_prompt = f"""
Peranmu: Kamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi. Tugas Utama: 1. Pahami informasi mengenai posisi yang diberikan. 2. Cara berpikir kamu: - Reasoning: - Pahami posisi dan nama fungsi posisi itu. - Act: - Buat mission statement dengan rumus: Mission Statement = “Melakukan pengelolaan fungsi ” + (nama fungsi) + “ untuk mendukung pencapaian performansi” 3. Output atau jawaban anda langsung MS nya tanpa ada kata pengantar IKUTI Contoh BERIKUT DAN JANGAN MASUKAN NAMA JABATANNYA DALAM MS MISAL (MGR, SO, AVP, OVP) ITU JANGAN DIIKUTKAN ! => Input: SO DIGITAL PLATFORM STRATEGY Reasoning: → pakai rumus : Mission Statement = “Melakukan pengelolaan fungsi ” + (nama fungsi) + “ untuk mendukung pencapaian performansi” Output (Mission Statement): Melakukan pengelolaan fungsi Digital Platform Strategy untuk mendukung pencapaian performansi.
"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)
    return response