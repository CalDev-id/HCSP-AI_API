
from typing import List
from llm.apilogy_runtime import ApilogyRunTime
from typing import Optional    
import re
import json

def jr_agent(nama_posisi: str, retrieve_data: List[dict]):
    apilogy_run = ApilogyRunTime()

    if not retrieve_data:
      context_text = "Tidak ada konteks pasal relevan."
    else:
      context_parts = []
      for record in retrieve_data:
          job_responsibilities = record.get("job_responsibilities", "")
          context_parts.append(f"{job_responsibilities}\n\n")
        
      context_text = "\n\n".join(context_parts)

    user_prompt = f"""
Berikut adalah daftar job responsibility dari posisi atasan. 
Tolong ubah menjadi JR sesuai aturan, lalu bagikan secara merata ke posisi bawahan yang paling relevan. 
Jika ada sisa, distribusikan lagi agar semua job responsibility terbagi tanpa sisa dan tidak ada yang duplikat.

📋 Job Responsibilities:
{context_text}

📌 Posisi Bawahan yang tersedia:
{nama_posisi}

Hasil akhir wajib dalam format JSON seperti yang sudah dijelaskan di sistem prompt.
"""


    system_prompt = """
Kamu adalah asisten analisis organisasi yang sangat teliti. 
Tugasmu adalah membuat dan membagi *Job Responsibilities (JR)* dari posisi atasan kepada beberapa posisi bawahan yang tersedia.

Tugasmu adalah membuat Job Responsibilities (JR). Ikuti aturan ketat berikut:

1️⃣ Rumus JR = **Kata Kerja + Fungsi/ Aktivitas/ Produk**.  
2️⃣ **DILARANG KERAS** memotong, meringkas, menambah, atau mengubah isi narasi asli tugas atasan.  
   Kamu hanya boleh mengganti kata kerja di bagian depan menjadi **kata kerja managerial** yang sesuai dengan band posisi.  
3️⃣ **Satu tugas atasan = satu JR utuh.** Tidak boleh satu tugas dipecah menjadi dua JR, dan tidak boleh dua tugas digabung menjadi satu JR.  
4️⃣ Semua tugas atasan **HARUS HABIS TERDISTRIBUSI** ke posisi bawahan yang paling relevan.  
   Tidak boleh ada satu pun tugas yang tertinggal.  
5️⃣ Setelah selesai membagi, **hitung total JR di seluruh posisi** dan pastikan totalnya = jumlah tugas atasan.  
   Jika jumlah JR ≠ jumlah tugas atasan, hasilmu dianggap SALAH dan harus diperbaiki.  
6️⃣ Pastikan **relevansi kuat** antara nama posisi dan aktivitas utama dari tugas tersebut.  
7️⃣ **Bagi jumlah JR secara merata** ke seluruh posisi bawahan.  
   Jika jumlahnya tidak bisa dibagi rata, bagikan sisa tugas secara adil ke posisi lain agar semua tugas terdistribusi.  
8️⃣ Tidak boleh ada duplikasi antar posisi.  
9️⃣ Output wajib berupa **JSON array valid**, **tanpa narasi, reasoning, catatan, atau teks tambahan**.

📘 Format JSON yang wajib digunakan:
[
  {
    "posisi": "nama posisi",
    "jr": "• Job Responsibility 1 \\n • Job Responsibility 2 \\n • Job Responsibility 3"
  },
  ...
]

Pastikan format JSON compacted dan valid seperti contoh:
[{"posisi":"Manager Platform Integration & Automation","jr":["Menilai efisiensi proses integrasi platform AI dan core IT platform","Memonitor pengelolaan capability platform AI untuk mendukung efisiensi bisnis"]},
{"posisi":"Manager Security Platform Management","jr":["Memastikan implementasi security platform sesuai kebijakan keamanan Perusahaan"]}]

🔹 Pedoman Kata Kerja:
- **Managerial / Manager:** Mencapai, Menilai, Menarik, Memastikan, Mengevaluasi, Mengidentifikasi, Meningkatkan, Menerapkan, Mengatasi, Memelihara, Memonitor, Mereview, Menetapkan, Menspesifikasi, Menstandart.
- **Non-Managerial:** Memeriksa, Membandingkan, Menyebarkan, Mengumpulkan, Menginformasikan, Memberitakan, Mengadakan, Memperoleh, Mengoperasikan, Melaksanakan, Menyajikan, Memproses, Menghasilkan, Menyampaikan, Menyediakan.

Ingat: hasil akhir hanya berupa JSON array valid sesuai format di atas, tidak boleh ada penjelasan tambahan apa pun.
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)
    
    if response:
        job_responsibilities = response.strip()

        job_responsibilities = job_responsibilities.replace("- ", "• ")

        try:
            # Kalau AI mengembalikan JSON string
            parsed = json.loads(job_responsibilities)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]
        except json.JSONDecodeError:
            # Kalau tidak bisa di-parse jadi JSON, bungkus jadi list
            return [{"posisi": "Unknown", "jr": job_responsibilities}]
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."
