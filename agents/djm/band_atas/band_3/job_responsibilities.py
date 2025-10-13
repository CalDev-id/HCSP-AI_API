
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
    print(nama_posisi)
    print("--------------------------------")
    print(context_text)
    user_prompt = f"""

Buatkan json berisi minimal satu Job Responsibilities (JR) untuk setiap posisi bawahan berikut, dan pastikan semua tugas atasan di bawah ini telah habis terbagi ke posisi bawahannya secara utuh,relevan dan tidak ada posisi terlewat, JIKA ADA TUGAS ATASAN YANG BELUM TERBAGI KE MANAGER MAKA JAWABAN ANDA SALAH DAN HARUS DIULANG !. Berikut Nama Posisi bawahan: {nama_posisi}; Berikut daftar tugas dari atasan (wajib semuanya terbagi tanpa dipotong narasinya):{context_text} . apapun hasil think anda maka outputnya tolong Gunakan format ouput sesuai contoh JSON, jangan beri **Note:** apapun yang terjadi

"""

    system_prompt = """
Tugasmu adalah membuat json berisi Job Responsibilities (JR). Ikuti aturan ketat berikut: 1) Rumus JR = Kata Kerja + Fungsi/ Aktivitas/ Produk. 2) DILARANG KERAS memotong, meringkas, menambah, atau mengubah isi narasi asli tugas atasan dan Kamu hanya boleh mengganti dengan paksa kata kerja di bagian depan kalimat tugas atasan menjadi kata kerja band III Managerial seseuai dengan pedoman kata kerja. 3) Pedoman Kata Kerja III Managerial : (Mencapai, Menilai, Menarik, Memastikan, Mengevaluasi, Mengidentifikasi, Meningkatkan, Menerapkan, Mengatasi, Memelihara, Memantau, Meninjau, Menetapkan, Menspesifikasi, Menstandarkan). 4) Satu tugas atasan = satu JR utuh. Tidak boleh satu tugas dipecah menjadi dua JR, dan tidak boleh dua tugas digabung menjadi satu JR. 5) Semua tugas atasan HARUS HABIS TERDISTRIBUSI ke posisi bawahan yang paling relevan. JIKA TUGAS ATASAN TIDAK HABIS TERBAGI KE BAWAHANNYA MAKA JAWABAN ANDA SALAH DAN HARUS DIBAGI ULANG. Tidak boleh ada satu pun tugas atasan yang tersisa artinya setiap tugas atasan harus dibagi secara tepat sesuai dengan fungsi posisi bawahannya. pastikan bahwa setiap tugas atasan sudah terbagi ke posisi bawahan yang tepat untuk menanganinya dan menjalankannya. 6) JIKA TUGAS ATASAN HANYA SATU, MAKA SELURUH TUGAS BAWAHANNYA JUGA AKAN SAMA DENGAN SATU TUGAS ATASAN ITU. 7) JIKA NAMA FUNGSI DARI POSISI BAWAHANNYA SAMA, MAKA TUGAS NYA JUGA AKAN SAMA, SEHINGGA TUGAS MANAGER HELPDESK 1 = TUGAS MANAGER HELPDESK 2 DAN SETERUSNYA. 8) Setelah selesai membagi, pastikan seluruh tugas Atasan terdistribusi semua dengan baik dan setiap posisi bawahan telah mendapatkan tugas. jika ada posisi yang terlewat atau ada posisi bawahan yang tidak mendapat tugas maka jawaban anda salah dan ulangi ! 9) Pastikan relevansi kuat antara nama posisi bawahan dan aktivitas utama dari tugas atasan tersebut, Jika tugas dari atasan tidak memiliki relevansi langsung dengan bawahan mana pun, Anda harus tetap menugaskannya secara paksa kepada bawahan yang memiliki fungsi kerja paling mirip atau paling mendekati relevansi dengan tugas tersebut. 10) please minta tolong apapun hasilnya tolong untuk menggunakan format output JSON compacted seperti berikut, ulangi jawabanmu jika bukan dalam bentuk json seperti ini: [{"posisi":"Manager Platform Integration & Automation", "jr": "- Menilai efisiensi proses integrasi platform AI dan core IT platform \n, - Memonitor pengelolaan capability platform AI untuk mendukung efisiensi bisnis"},{"posisi":"Manager Security Platform Management", "jr": "- Memastikan implementasi security platform sesuai kebijakan keamanan Perusahaan"}]. 11) Jangan menambahkan reasoning, catatan, atau teks di luar struktur JSON.
"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)
    
    if response:
        job_responsibilities = response.strip()

        job_responsibilities = job_responsibilities.replace("- ", "• ")

        try:
            # Kalau AI mengembalikan JSON string
            print("--------------------------------------")
            print(job_responsibilities)
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
