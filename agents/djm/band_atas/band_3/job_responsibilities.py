
from typing import List
from llm.apilogy_runtime import ApilogyRunTime
from typing import Optional    
import re

def jr_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict], jr_kepake: Optional[List[str]] = None):
    apilogy_run = ApilogyRunTime()

    if not retrieve_data:
      context_text = "Tidak ada konteks pasal relevan."
    else:
      context_parts = []
      for record in retrieve_data:
          job_responsibilities = record.get("job_responsibilities", "")
          context_parts.append(f"{job_responsibilities}\n\n")
        
      context_text = "\n\n".join(context_parts)

    if jr_kepake:
        jr_kepake_text = "\n\n".join(
            f"{jr}" for jr in jr_kepake
        )
    else:
        jr_kepake_text = ""

    final_text = build_final_text(context_text, jr_kepake_text)
    print("FINAL TEXT JR AGENT:", final_text)
    print("============================================================================================================")
    jr_points_count = count_jr_points(context_text)
    user_prompt = f"""

Buatkan minimal satu dan maksimal tiga Job Responsibilities (jika tugas atasan berikut > 5 ) untuk posisi berikut [DILARANG KERAS DUPLIKASI TUGAS YANG SUDAH DIAMBIL POSISI ATAU MANAGER LAIN] => Nama Posisi : {nama_posisi}. Band Posisi : {band_posisi}. Berikut List tugas-tugas atasan dari posisi tersebut dengan jumlah tugas sebanyak :{jr_points_count} berikut tugas-tugas atasannya => {final_text}. Instruksi: - BACA SEMUA list tugas atasan yang diberikan, pilih minimal satu dan paling banyak tiga tugas (jika tugas atasan berjumlah lebih dari 5) yang paling relevan dengan nama fungsi posisi tersebut. - Ubah kata kerja depan dengan kata kerja managerial. Jangan menambah atau mengubah isi aktivitas utama selain kata kerja depannya. - Hasil akhir berupa list (min 1 dan max 3) Job Responsibilities dalam format list item. - Setiap list item dipisahkan dengan tanda strip (-). - Tidak perlu menambahkan kata pengantar, penjelasan, atau penutup. Output yang diharapkan: - ... - ... - ... , TIDAK di-BOLD, DAN JANGAN BERI CATATAN APAPUN
"""

    system_prompt = f"""
Tugasmu adalah membuat Job Responsibilities (JR). Ikuti langkah berikut: 1) Rumus JR = [Kata Kerja + Aktivitas utama dari atasan.] Gunakan kata kerja sesuai pedoman band/posisi. 2) JR diturunkan dari JR atasan yang diberikan user. Jangan ubah atau menambah narasi aktivitas utama, cukup hanya ubah kata kerja di depan. 3) Khusus untuk Band Posisi 3: JR wajib diambil dari JR atasan yang diberikan user, IF [HITUNG JUMLAH TUGAS ATASAN YANG DIBERIKAN, JIKA TUGAS ATASAN YANG DIBERIKAN USER KURANG DARI 5 POIN ATAU SAMA DENGAN 5 (<=5), MAKSIMAL 2 TUGAS Untuk tiap posisi manager TIDAK BOLEH LEBIH !]. ELSE (tugas atasan >5) [selanjutnya pilih Maximal tiga tugas atau minimal satu tugas yang paling dan sangat relevan dengan nama fungsi atau nama posisi]. pastikan tugasnya sangat relevan dan sangat sesuai antara nama posisi/fungsi dengan aktivitas utama yang dipilih atau bisa juga cari aktivitas utama yang memuat kata kunci spesifik dari nama posisinya misalnya, untuk posisi Manager CEM Operation Support maka cari di list tugas atasan yang cocok untuk bidang Operation Support. Misalnya lagi untuk posisi Manager OSS Fulfillment & Order Management Platform maka cari di list tugas atasan yang cocok untuk bidang OSS Fulfillment & Order Management. PERHATIKAN ! [SANGAT DILARANG MENGAMBIL TUGAS ATASAN YANG SUDAH DIAMBIL OLEH MANAGER LAIN, TIDAK BOLEH TERJADI DUPLIKASI TUGAS] KONDISI LAIN, JIKA TUGAS ATASAN NYA SUDAH HABIS DIAMBIL SEMUA, AMBIL SATU SAJA YANG PALING RELEVAN DAN JANGAN BERIKAN CATATAN APAPUN! . 4) Output: Hasilkan terdiri dari minimal satu  sampai maksimal tiga (jika tugas atasan >=5) JR final yang spesifik sesuai band posisi 3 dan nama fungsi posisinya, TIDAK BOLEH LEBIH. Act (Output yang Harus Dihasilkan): Hasilkan daftar Job Responsibilities dalam format list Specific JR berdasarkan band/posisi dan kata kerja pedoman yang sesuai dengan JR atasannya dan TIDAK DI BOLD, contoh format: - [Specific Responsibility 1 (minimal)] - [Specific Responsibility 2] - [Specific Responsibility 3 (maksimal)]. || Pedoman Kata Kerja BP 3 BP 3 MANAGERIAL/MANAGER : Mencapai, Menilai [kompetensi], Menarik, Memastikan, Mengevaluasi, Mengidentifikasi, Meningkatkan, Menerapkan, Mengatasi, Memelihara, Memonitor, Mereview, Menetapkan [goals], Menspesifikasi, Menstandart. BP 3 NON MANAGERIAL : Memeriksa, Membandingkan, Menyebarkan, Mengumpulkan, Menginformasikan, Memberitakan, Mengadakan, Memperoleh, Mengoperasikan, Melaksanakan, Menyajikan, Memproses, Menghasilkan, Menyampaikan, Menyediakan || Contoh Alur Berpikir: INPUT : MGR ANALYTICS & VISUALIZATION PLATFORM (Band III Managerial) -> BACA SEMUA list Tugas-Tugas Atasan yang diberikan oleh user -> CARI tugas atasan YANG SESUAI DAN FIT UNTUK POSISI MGR ANALYTICS & VISUALIZATION PLATFORM DENGAN MELIHAT FUNGSI POSISI YAITU ANALYTICS & VISUALIZATION -> OUTPUT: - tugas spesifik MGR ANALYTICS & VISUALIZATION PLATFORM ke 1 - tugas spesifik MGR ANALYTICS & VISUALIZATION PLATFORM ke 2 - tugas spesifik MGR ANALYTICS & VISUALIZATION PLATFORM 3.
"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)
    
    if response:
        job_responsibilities = response.strip()

        job_responsibilities = job_responsibilities.replace("- ", "• ")
        job_responsibilities = job_responsibilities.replace("'", "").replace("[", "").replace("]", "")

        return job_responsibilities
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."

def build_final_text(jr_atasan: str, jr_last: str) -> str:
    final_text = jr_atasan

    if jr_last and jr_last.strip():
        final_text = (
            f"{jr_atasan} || SANGAT DILARANG mengambil lagi poin poin tugas berikut "
            f"karena SUDAH diambil oleh manager lain, ambil poin tugas atasan relevan "
            f"yang lainnya SELAIN poin tugas berikut ini : {jr_last}"
        )

    final_text = re.sub(r"\n+", ". ", final_text) 
    final_text = re.sub(r"\s+", " ", final_text) 
    final_text = re.sub(r"\. \.", ".", final_text) 
    final_text = final_text.strip()
    final_text = final_text.replace("'", "")  

    return final_text

def count_jr_points(jr_text: str) -> int:
    kalimat_list = re.split(r"\n|^-|•", jr_text, flags=re.MULTILINE)
    kalimat_list = [s.strip() for s in kalimat_list if s.strip()]
    return len(kalimat_list)
