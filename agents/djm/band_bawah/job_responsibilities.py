from typing import List
from llm.apilogy_runtime import ApilogyRunTime
from llm.groq_runtime import GroqRunTime
import json

def jr_agent(nama_posisi: str, retrieve_data: List[dict], field_name: str = "job_responsibilities"):
    apilogy_run = ApilogyRunTime()
    groq = GroqRunTime()

    if not retrieve_data:
        context_text = "Tidak ada konteks relevan."
    else:
        context_parts = []
        for record in retrieve_data:
            field_value = record.get(field_name, "")
            if field_value:
                context_parts.append(field_value.strip())

        context_text = "\n\n".join(context_parts) if context_parts else f"Tidak ada data pada field '{field_name}'."
    print(nama_posisi)
    print("--------------------------------")
    print("jr atasan : ",context_text)
    user_prompt = f"""

Buatkan minimal 1 Job Responsibilities (JR) untuk tiap posisi berikut, 
dan pastikan semua tugas atasan di bawah ini telah habis terbagi ke posisi bawahannya secara utuh dan relevan. 
Jumlah total JR terbagi ke posisi bawahan wajib sama dengan jumlah tugas atasan yang diberikan diawal, 
tidak boleh kurang dan tidak boleh lebih. Nama Posisi bawahan: {nama_posisi}; 
Berikut daftar tugas dari atasan (wajib semuanya terbagi tanpa dipotong narasinya):{context_text}.
Gunakan format JSON compacted. Poin JR boleh berbentuk bullet (•) jika diperlukan.
"""

    system_prompt = """
Tugasmu adalah membuat Job Responsibilities (JR). Ikuti aturan ketat berikut:

1. Rumus JR = Kata Kerja + Fungsi/ Aktivitas/ Produk.
2. DILARANG KERAS memotong, meringkas, menambah, atau mengubah isi narasi asli tugas atasan.
   Kamu hanya boleh mengganti kata kerja di bagian depan menjadi kata kerja band 4, 5, 6, dan Senior Officer (SO).
3. Satu tugas atasan = satu JR utuh.
   Tidak boleh satu tugas dipecah menjadi dua JR, dan tidak boleh dua tugas digabung menjadi satu JR.
4. Semua tugas atasan HARUS HABIS TERDISTRIBUSI ke posisi paling relevan.
   Tidak boleh ada satu pun tugas yang tersisa.
   Jika jumlah JR ≠ jumlah tugas atasan, hasilmu dianggap SALAH dan harus diperbaiki sampai jumlahnya sama persis.
5. Setelah selesai membagi, hitung total JR di seluruh posisi dan pastikan totalnya = jumlah tugas atasan.
6. Pastikan relevansi kuat antara nama posisi dan aktivitas utama dari tugas tersebut.
7. Gunakan format JSON compacted berikut (tanpa tambahan teks di luar JSON):

[
  {
    "posisi": "nama posisi",
    "jr": "• Job Responsibility 1 \\n • Job Responsibility 2 \\n • Job Responsibility 3"
  },
  ...
]

8. Jangan menambahkan reasoning, catatan, atau teks di luar struktur JSON.
9. Pedoman Kata Kerja Band 4, 5, 6, dan Senior Officer (SO):
   (Memeriksa, Membandingkan, Menyebarkan, Mengumpulkan, Menginformasikan,
   Memberitakan, Mengadakan, Memperoleh, Mengoperasikan, Melaksanakan,
   Menyajikan, Memproses, Menghasilkan, Menyampaikan, Menyediakan).
"""


    # response = apilogy_run.generate_response(system_prompt, user_prompt)
    response = groq.generate_response(system_prompt, user_prompt)

    if response:
        job_responsibilities = response.strip()

        job_responsibilities = job_responsibilities.replace("- ", "• ")

        try:
            print("--------------------------------------")
            print("jr generated : ",job_responsibilities)
            parsed = json.loads(job_responsibilities)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]
        except json.JSONDecodeError:
            return [{"posisi": "Unknown", "jr": job_responsibilities}]
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."
