
from typing import List
from llm.apilogy_runtime import ApilogyRunTime
from llm.groq_runtime import GroqRunTime
from typing import Optional    
import re
import json

def jr_agent(nama_posisi: str, retrieve_data: List[dict]):
    apilogy_run = ApilogyRunTime()
    groq = GroqRunTime()

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
    print("jr atasan : ",context_text)
    user_prompt = f"""

Buatkan json berisi minimal satu Job Responsibilities (JR) untuk setiap posisi bawahan berikut, dan pastikan semua tugas atasan di bawah ini telah habis terbagi ke posisi bawahannya secara utuh,relevan dan tidak ada posisi terlewat, JIKA ADA TUGAS ATASAN YANG BELUM TERBAGI KE MANAGER MAKA JAWABAN ANDA SALAH DAN HARUS DIULANG !. Berikut Nama Posisi bawahan: {nama_posisi}; Berikut daftar tugas dari atasan (wajib semuanya terbagi tanpa dipotong narasinya):{context_text} . apapun hasil think anda maka outputnya tolong Gunakan format ouput sesuai contoh JSON, jangan beri **Note:** apapun yang terjadi

"""

    system_prompt = """
Tugasmu adalah membuat json berisi Job Responsibilities (JR). Ikuti aturan ketat berikut: 1) Rumus JR = Kata Kerja + Fungsi/ Aktivitas/ Produk. 2) DILARANG KERAS memotong, meringkas, menambah, atau mengubah isi narasi asli tugas atasan dan Kamu hanya boleh mengganti dengan paksa kata kerja di bagian depan kalimat tugas atasan menjadi kata kerja band III Managerial seseuai dengan pedoman kata kerja. 3) Pedoman Kata Kerja III Managerial : (Mencapai, Menilai, Menarik, Memastikan, Mengevaluasi, Mengidentifikasi, Meningkatkan, Menerapkan, Mengatasi, Memelihara, Memantau, Meninjau, Menetapkan, Menspesifikasi, Menstandarkan). 4) Satu tugas atasan = satu JR utuh. Tidak boleh satu tugas dipecah menjadi dua JR, dan tidak boleh dua tugas digabung menjadi satu JR. 5) Semua tugas atasan HARUS HABIS TERDISTRIBUSI ke posisi bawahan yang paling relevan. JIKA TUGAS ATASAN TIDAK HABIS TERBAGI KE BAWAHANNYA MAKA JAWABAN ANDA SALAH DAN HARUS DIBAGI ULANG. Tidak boleh ada satu pun tugas atasan yang tersisa artinya setiap tugas atasan harus dibagi secara tepat sesuai dengan fungsi posisi bawahannya. pastikan bahwa setiap tugas atasan sudah terbagi ke posisi bawahan yang tepat untuk menanganinya dan menjalankannya. 6) JIKA TUGAS ATASAN HANYA SATU, MAKA SELURUH TUGAS BAWAHANNYA JUGA AKAN SAMA DENGAN SATU TUGAS ATASAN ITU. 7) JIKA NAMA FUNGSI DARI POSISI BAWAHANNYA SAMA, MAKA TUGAS NYA JUGA AKAN SAMA, SEHINGGA TUGAS MANAGER HELPDESK 1 = TUGAS MANAGER HELPDESK 2 DAN SETERUSNYA. 8) Setelah selesai membagi, pastikan seluruh tugas Atasan terdistribusi semua dengan baik dan setiap posisi bawahan telah mendapatkan tugas. jika ada posisi yang terlewat atau ada posisi bawahan yang tidak mendapat tugas maka jawaban anda salah dan ulangi ! 9) Pastikan relevansi kuat antara nama posisi bawahan dan aktivitas utama dari tugas atasan tersebut, Jika tugas dari atasan tidak memiliki relevansi langsung dengan bawahan mana pun, Anda harus tetap menugaskannya secara paksa kepada bawahan yang memiliki fungsi kerja paling mirip atau paling mendekati relevansi dengan tugas tersebut. 10) please minta tolong apapun hasilnya tolong untuk menggunakan format output JSON compacted seperti berikut, ulangi jawabanmu jika bukan dalam bentuk json seperti ini: [{"posisi":"Manager Platform Integration & Automation", "jr": "- Menilai efisiensi proses integrasi platform AI dan core IT platform \n, - Memonitor pengelolaan capability platform AI untuk mendukung efisiensi bisnis"},{"posisi":"Manager Security Platform Management", "jr": "- Memastikan implementasi security platform sesuai kebijakan keamanan Perusahaan"}]. 11) Jangan menambahkan reasoning, catatan, atau teks di luar struktur JSON.
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

















# from typing import List
# from llm.apilogy_runtime import ApilogyRunTime
# from typing import Optional    
# import re

# def jr_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict], jr_kepake: Optional[List[str]] = None):
#     apilogy_run = ApilogyRunTime()

#     if not retrieve_data:
#       context_text = "Tidak ada konteks pasal relevan."
#     else:
#       context_parts = []
#       for record in retrieve_data:
#           job_responsibilities = record.get("job_responsibilities", "")
#           context_parts.append(f"{job_responsibilities}\n\n")
        
#       context_text = "\n\n".join(context_parts)

#     if jr_kepake:
#         jr_kepake_text = "\n\n".join(
#             f"{jr}" for jr in jr_kepake
#         )
#     else:
#         jr_kepake_text = ""

#     final_text = build_final_text(context_text, jr_kepake_text)
#     jr_points_count = count_jr_points(context_text)
#     user_prompt = f"""

# Buatkan minimal satu dan maksimal tiga Job Responsibilities (jika tugas atasan berikut > 5 ) untuk posisi berikut [DILARANG KERAS DUPLIKASI TUGAS YANG SUDAH DIAMBIL POSISI ATAU MANAGER LAIN] => Nama Posisi : {nama_posisi}. Band Posisi : {band_posisi}. Berikut List tugas-tugas atasan dari posisi tersebut dengan jumlah tugas sebanyak :{jr_points_count} berikut tugas-tugas atasannya => {final_text}. Instruksi: - BACA SEMUA list tugas atasan yang diberikan, pilih minimal satu dan paling banyak tiga tugas (jika tugas atasan berjumlah lebih dari 5) yang paling relevan dengan nama fungsi posisi tersebut. - Ubah kata kerja depan dengan kata kerja managerial. Jangan menambah atau mengubah isi aktivitas utama selain kata kerja depannya. - Hasil akhir berupa list (min 1 dan max 3) Job Responsibilities dalam format list item. - Setiap list item dipisahkan dengan tanda strip (-). - Tidak perlu menambahkan kata pengantar, penjelasan, atau penutup. Output yang diharapkan: - ... - ... - ... , TIDAK di-BOLD, DAN JANGAN BERI CATATAN APAPUN
# """

#     system_prompt = f"""
# Tugasmu adalah membuat Job Responsibilities (JR). Ikuti langkah berikut: 1) Rumus JR = [Kata Kerja + Aktivitas utama dari atasan.] Gunakan kata kerja sesuai pedoman band/posisi. 2) JR diturunkan dari JR atasan yang diberikan user. Jangan ubah atau menambah narasi aktivitas utama, cukup hanya ubah kata kerja di depan. 3) Khusus untuk Band Posisi 3: JR wajib diambil dari JR atasan yang diberikan user, IF [HITUNG JUMLAH TUGAS ATASAN YANG DIBERIKAN, JIKA TUGAS ATASAN YANG DIBERIKAN USER KURANG DARI 5 POIN ATAU SAMA DENGAN 5 (<=5), MAKSIMAL 2 TUGAS Untuk tiap posisi manager TIDAK BOLEH LEBIH !]. ELSE (tugas atasan >5) [selanjutnya pilih Maximal tiga tugas atau minimal satu tugas yang paling dan sangat relevan dengan nama fungsi atau nama posisi]. pastikan tugasnya sangat relevan dan sangat sesuai antara nama posisi/fungsi dengan aktivitas utama yang dipilih atau bisa juga cari aktivitas utama yang memuat kata kunci spesifik dari nama posisinya misalnya, untuk posisi Manager CEM Operation Support maka cari di list tugas atasan yang cocok untuk bidang Operation Support. Misalnya lagi untuk posisi Manager OSS Fulfillment & Order Management Platform maka cari di list tugas atasan yang cocok untuk bidang OSS Fulfillment & Order Management. PERHATIKAN ! [SANGAT DILARANG MENGAMBIL TUGAS ATASAN YANG SUDAH DIAMBIL OLEH MANAGER LAIN, TIDAK BOLEH TERJADI DUPLIKASI TUGAS] KONDISI LAIN, JIKA TUGAS ATASAN NYA SUDAH HABIS DIAMBIL SEMUA, AMBIL SATU SAJA YANG PALING RELEVAN DAN JANGAN BERIKAN CATATAN APAPUN! . 4) Output: Hasilkan terdiri dari minimal satu  sampai maksimal tiga (jika tugas atasan >=5) JR final yang spesifik sesuai band posisi 3 dan nama fungsi posisinya, TIDAK BOLEH LEBIH. Act (Output yang Harus Dihasilkan): Hasilkan daftar Job Responsibilities dalam format list Specific JR berdasarkan band/posisi dan kata kerja pedoman yang sesuai dengan JR atasannya dan TIDAK DI BOLD, contoh format: - [Specific Responsibility 1 (minimal)] - [Specific Responsibility 2] - [Specific Responsibility 3 (maksimal)]. || Pedoman Kata Kerja BP 3 BP 3 MANAGERIAL/MANAGER : Mencapai, Menilai [kompetensi], Menarik, Memastikan, Mengevaluasi, Mengidentifikasi, Meningkatkan, Menerapkan, Mengatasi, Memelihara, Memonitor, Mereview, Menetapkan [goals], Menspesifikasi, Menstandart. BP 3 NON MANAGERIAL : Memeriksa, Membandingkan, Menyebarkan, Mengumpulkan, Menginformasikan, Memberitakan, Mengadakan, Memperoleh, Mengoperasikan, Melaksanakan, Menyajikan, Memproses, Menghasilkan, Menyampaikan, Menyediakan || Contoh Alur Berpikir: INPUT : MGR ANALYTICS & VISUALIZATION PLATFORM (Band III Managerial) -> BACA SEMUA list Tugas-Tugas Atasan yang diberikan oleh user -> CARI tugas atasan YANG SESUAI DAN FIT UNTUK POSISI MGR ANALYTICS & VISUALIZATION PLATFORM DENGAN MELIHAT FUNGSI POSISI YAITU ANALYTICS & VISUALIZATION -> OUTPUT: - tugas spesifik MGR ANALYTICS & VISUALIZATION PLATFORM ke 1 - tugas spesifik MGR ANALYTICS & VISUALIZATION PLATFORM ke 2 - tugas spesifik MGR ANALYTICS & VISUALIZATION PLATFORM 3.
# """
#     response = apilogy_run.generate_response(system_prompt, user_prompt)
    
#     if response:
#         job_responsibilities = response.strip()

#         job_responsibilities = job_responsibilities.replace("- ", "• ")
#         job_responsibilities = job_responsibilities.replace("'", "").replace("[", "").replace("]", "")

#         return job_responsibilities
#     else:
#         print("Tidak ada respons dari AI.")
#         return "Tidak ada respons dari AI."

# def build_final_text(jr_atasan: str, jr_last: str) -> str:
#     final_text = jr_atasan

#     if jr_last and jr_last.strip():
#         final_text = (
#             f"{jr_atasan} || SANGAT DILARANG mengambil lagi poin poin tugas berikut "
#             f"karena SUDAH diambil oleh manager lain, ambil poin tugas atasan relevan "
#             f"yang lainnya SELAIN poin tugas berikut ini : {jr_last}"
#         )

#     final_text = re.sub(r"\n+", ". ", final_text) 
#     final_text = re.sub(r"\s+", " ", final_text) 
#     final_text = re.sub(r"\. \.", ".", final_text) 
#     final_text = final_text.strip()
#     final_text = final_text.replace("'", "")  

#     return final_text

# def count_jr_points(jr_text: str) -> int:
#     kalimat_list = re.split(r"\n|^-|•", jr_text, flags=re.MULTILINE)
#     kalimat_list = [s.strip() for s in kalimat_list if s.strip()]
#     return len(kalimat_list)