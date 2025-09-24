from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ja_agent(nama_posisi: str, retrieve_data: List[dict], job_responsibilities: str, mission_statement: str):

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
    sekarang, buatkan mission statement untuk posisi berikut :

Nama Posisi : {nama_posisi}


Mission Statement hanya berupa teks narasi langsung sebutkan misinya tanpa ada kata pengantarnya, tanpa penanda seperti (-/*), dan tidak dibold !

sekarang,buatkan Job Authorization untuk posisi berikut berdasarkan MS dan JR nya :
Nama Posisi : {nama_posisi}
Job Responsibility Posisi : {job_responsibilities}
Mission Statement Posisi : {mission_statement}

Outputnya langsung berupa list item dari JR tanpa kata pengantar, tanpa penanda seperti (-/*) dan tidak dibold !
    """

    system_prompt = f"""
Peranmu:
Kamu adalah asisten AI HC yang membantu menyusun Job Authorities (JA) untuk setiap posisi.

Definisi JA:
- JA adalah kewenangan yang diberikan kepada pemangku posisi untuk menjalankan Job Responsibility agar dapat mencapai Mission Statement tanpa bantuan atasan.
- JA merupakan tingkat keputusan yang bisa dan harus diambil pemangku posisi.
- khusus untuk posisi SGM, JA diambil langsung dari kewenangan yang tertulis dalam peraturan yang diambil dari **database perusahaan**

Rumus Aspek Utama JA:
Setiap posisi harus memiliki JA yang mencakup aspek berikut:
1. Penentuan prioritas pekerjaan/pembiayaan.
2. Akses aplikasi.
3. Sumber data yang digunakan.
4. Metodologi kerja.
5. Penentuan target kerja unit dan staf (untuk posisi managerial).
6. Penilaian performansi/kompetensi staf (untuk posisi managerial).
7. Pengembangan kompetensi diri dan/atau staf.

Instruksi ReAct:
1. Reasoning:
   - Pahami nama posisi yang diberikan.
   - Identifikasi apakah posisi tersebut managerial atau non-managerial.
  - Ambil konteks → gunakan **database perusahaan** untuk memahami posisi, unit kerja, dan wewenang posisi tersebut, bukan **aktivitas utama melainkan wewenang**
  - Untuk Band posisi 1 WAJIB AMBIL SEMUA POIN UTUH yang ada di **database perusahaan** setelah kalimat berikut "(nama posisi) diberi kewenangan antara lain untuk". Ambil semua poinnya dan jangan ada yang diubah
   - untuk **posisi selain SGM** pahami mission statement dan job responsibility yang diberikan user terkait posisi tersebut.
   - Tentukan aspek JA yang relevan dari daftar di atas dan pastikan sesuai dengan mission statement dan job responsibility posisi dari user.
2. Act:
   - Hasilkan output berupa daftar Job Authorities (JA) dalam bentuk poin-poin yang jelas, sesuai rumus, dalam list dan tidak dibold.
   - Jika posisi managerial, sertakan poin terkait penetapan target staf, penilaian kinerja staf, dan pengembangan staf.
   - Jika posisi non-managerial, fokus pada kewenangan yang mendukung pekerjaan individu (tanpa poin tentang staf).

------------------------------------------------------------
IKUTI CONTOH BERIKUT untuk LLM berpikir :
yang ditamplikan hanya output saja !

- Input:
Posisi - SM SHARED SERVICE PLANNING & GOVERNANCE

-> Reasoning:
- Posisi "SM" (Senior Manager) adalah posisi managerial bukan SGM.
-> pahami Mission Statement dan Job responsibility yang diberikan user
- Harus mencakup seluruh aspek JA termasuk target staf, penilaian kinerja staf, dan pengembangan staf.

- Output (Job Authorities):
- Menentukan prioritas pembiayaan / pekerjaan.
- Memiliki hak akses atas aplikasi ESS / Enterprise Support System.
- Menetapkan sumber data.
- Menetapkan metodologi kerja.
- Menetapkan sasaran kinerja individu (staf).
- Menilai kinerja dan kompetensi individu (staf).
- Merekomendasikan program-program pengembangan staf.

------------------------------------------------------------

- Input:
Posisi - OFFICER DIGITAL PLATFORM STRATEGY

-> Reasoning:
- Posisi Officer adalah non-managerial BUKAN SGM.
-> pahami Mission Statement dan Job responsibility yang diberikan user
- Fokus hanya pada aspek kewenangan individu (tanpa staf).

- Output (Job Authorities):
- Menentukan prioritas pekerjaan sesuai lingkup tanggung jawab.
- Memiliki hak akses atas aplikasi Digital Platform Strategy.
- Menetapkan sumber data yang digunakan dalam pekerjaan.
- Menetapkan metodologi kerja sesuai standar unit.
- Mengembangkan kompetensi diri untuk mendukung pencapaian kinerja.

**database perusahaan** 
{context_text}
"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_authorities = response["choices"][0]["message"]["content"].strip()
        print(job_authorities)
        return job_authorities
    else:
        print("Tidak ada respons dari AI.")
        return ""



