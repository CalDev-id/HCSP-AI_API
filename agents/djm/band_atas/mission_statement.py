from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ms_agent(nama_posisi: str, band_posisi: str, retrieve_data: str):
    apilogy_run = ApilogyRunTime()
    
    context_text = retrieve_data if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""

Buatkan mission statement untuk posisi berikut: Nama Posisi: {nama_posisi} dengan band posisi nya: {band_posisi} Mission Statement hanya berupa teks narasi langsung, salin tanggung jawab yang diawali dengan \"Bertanggung Jawab\" bukan aktivitas utama dan seterusnya atau untuk deputy ambil selalu dari Pasal tanggung jawab deputy,format output : sajikan output tanpa kata pengantar, tanpa penanda seperti (-/*), dan tidak dibold! Berikut konteks yang dapat anda gunakan untuk membentuk mission statement dari posisi tersebut: {context_text}
"""

    system_prompt = f"""
Kamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi. Tugas: 1. penting, Tidak semua chunk perlu dipakai, cukup gunakan dan pahami chunk yang sumber pasalnya sesuai dengan nama fungsi posisi untuk memahami fungsi, unit kerja, dan aktivitas utamanya. 2. Pahami hubungan antara posisi dan band-nya. 3. Jika posisi memiliki BAND (BP) I atau II: - Reasoning: - Gunakan context chunk dengan sumber pasal yang sesuai dengan nama posisi tersebut untuk mencari informasi relevan mengenai posisi tersebut. - Dari informasi itu, cari tanggung jawab posisi tersebut di dalam chunk yang sumber pasalnya sesuai dengan nama fungsi posisi. - Act: - Buatkan mission statement dengan cara SALIN LANGSUNG tanggung jawab posisi tersebut di dalam PR Organisasi yang selalu dimulai dengan kata-kata \"Bertanggung Jawab\". 4. Khusus BAND POSISI 1 dengan NAMA POSISI DEPUTY: - Reasoning: - Gunakan context yang ada untuk mencari informasi relevan mengenai posisi tersebut. - Act: - Mission Statement Deputy diambil dari Pasal 7 ayat 3 poin b dalam PR Organisasi yang bersangkutan ditandai dengan kata \"Deputy Bertanggung Jawab Atas\". JANGAN AMBIL AKTIVITAS UTAMA, BERHENTI SAMPAI SAAT KETEMU AKTIVITAS UTAMA. BUKAN AKTIVITAS UTAMA YANG KAMU AMBIL TETAPI TANGGUNG JAWAB !. UNTUK DEPUTY, Jangan ambil dari poin yang sama untuk deputy lain yang nama fungsinya berbeda dengan sumber pasal. Output hanya berupa mission statement dalam bentuk teks paling banyak 2 sampai 3 kalimat narasi langsung, tanpa pengantar, tanpa penanda (-/*), dan tidak dibold.
"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        mission_statement = response["choices"][0]["message"]["content"].strip()
        return mission_statement
    else:
        print("Tidak ada respons dari AI.")
        return ""