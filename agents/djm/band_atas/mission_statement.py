from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ms_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[str]):
    apilogy_run = ApilogyRunTime()
    
    context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""

Buatkan mission statement untuk posisi berikut: Nama Posisi: {nama_posisi} dengan band posisi nya: {band_posisi} Mission Statement hanya berupa teks narasi langsung, salin tanggung jawab yang diawali dengan \"Bertanggung Jawab\" dan seterusnya atau untuk deputy ambil selalu dari Pasal 7 tanggung jawab deputy, tanpa kata pengantar, tanpa penanda seperti (-/*), tidak kapital dan tidak dibold! Berikut konteks yang dapat anda gunakan untuk membentuk mission statement dari posisi tersebut: {context_text}
"""

    system_prompt = f"""
Kamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi. Tugas: 1. Pahami informasi mengenai posisi yang diberikan. 2. Pahami hubungan antara posisi dan band-nya. 3. Jika posisi memiliki BAND (BP) I atau II: - Reasoning: - Gunakan context yang ada untuk mencari informasi relevan mengenai posisi tersebut. - Dari informasi itu, cari tanggung jawab posisi tersebut di dalam PR Organisasi. - Act: - Buatkan mission statement dengan cara SALIN LANGSUNG tanggung jawab posisi tersebut di dalam PR Organisasi yang selalu dimulai dengan kata-kata \"Bertanggung Jawab\". 4. Khusus BAND POSISI 1 dengan NAMA POSISI DEPUTY: - Reasoning: - Gunakan context yang ada untuk mencari informasi relevan mengenai posisi tersebut. - Act: - Mission Statement Deputy diambil dari Pasal 7 ayat 3 poin b dalam PR Organisasi yang bersangkutan ditandai dengan kata \"Deputy Bertanggung Jawab Atas\". - Jika ada deputy berikutnya ambil dari Pasal 7 Ayat 3 Poin c, dan seterusnya. Jangan ambil dari poin yang sama. Output hanya berupa mission statement dalam bentuk teks narasi langsung, tanpa pengantar, tanpa penanda (-/*), dan tidak dibold.

"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        mission_statement = response["choices"][0]["message"]["content"].strip()
        return mission_statement
    else:
        print("Tidak ada respons dari AI.")
        return ""