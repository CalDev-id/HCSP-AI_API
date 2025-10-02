from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ja_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict], job_responsibilities: str, mission_statement: str):

    apilogy_run = ApilogyRunTime()

    if not retrieve_data:
      context_text = "Tidak ada konteks pasal relevan."
    else:
      context_parts = []
      for record in retrieve_data:
          job_responsibilities = record.get("job_responsibilities", "")
          context_parts.append(f"Job Responsibilities: {job_responsibilities}\n\n")
        
      context_text = "\n\n".join(context_parts)

    user_prompt = f"""

    Buatkan Job Authorization untuk posisi berikut berdasarkan MS dan JR nya: \n Nama Posisi : {nama_posisi} \n Job Responsibility Posisi tersebut : {job_responsibilities}. \n Mission Statement Posisi tersebut :  {mission_statement}. \n\n Outputnya langsung berupa list item dari JA dan pisahkan dengan penanda seperti strip (-) serta tidak dibold!
    """


    system_prompt = f"""
Peranmu:\nKamu adalah asisten AI HC yang membantu menyusun Job Authorities (JA) untuk setiap posisi.\n\nDefinisi JA:\n- JA adalah kewenangan yang diberikan kepada pemangku posisi untuk menjalankan Job Responsibility agar dapat mencapai Mission Statement tanpa bantuan atasan.\n- JA merupakan tingkat keputusan yang bisa dan harus diambil pemangku posisi.\n- Untuk posisi SGM, JA diambil langsung dari kewenangan yang tertulis dalam peraturan yang diambil dari get_context.\n\nAspek utama JA:\n1. Penentuan prioritas pekerjaan/pembiayaan.\n2. Akses aplikasi.\n3. Sumber data yang digunakan.\n4. Metodologi kerja.\n5. Penentuan target kerja unit dan staf (khusus managerial).\n6. Penilaian performansi/kompetensi staf (khusus managerial).\n7. Pengembangan kompetensi diri dan/atau staf.\n\nInstruksi:\n1. Reasoning:\n   - Identifikasi apakah posisi managerial atau non-managerial.\n   - Ambil konteks get_context untuk posisi SGM (ambil seluruh kewenangan utuh).\n   - Untuk posisi selain SGM, pahami mission statement dan job responsibility yang diberikan.\n   - Tentukan aspek JA yang relevan sesuai daftar di atas.\n2. Act:\n   - Hasilkan output berupa daftar Job Authorities (JA) dalam bentuk poin-poin jelas, tanpa bold.\n   - Jika managerial → sertakan target staf, penilaian staf, dan pengembangan staf.\n   - Jika non-managerial → hanya aspek kewenangan individu.\n\nContoh:\nInput:\nPosisi - SM SHARED SERVICE PLANNING & GOVERNANCE\nOutput:\nMenentukan prioritas pembiayaan / pekerjaan.\nMemiliki hak akses atas aplikasi ESS / Enterprise Support System.\nMenetapkan sumber data.\nMenetapkan metodologi kerja.\nMenetapkan sasaran kinerja individu (staf).\nMenilai kinerja dan kompetensi individu (staf).\nMerekomendasikan program pengembangan staf.\n\nInput:\nPosisi - OFFICER DIGITAL PLATFORM STRATEGY\nOutput:\nMenentukan prioritas pekerjaan sesuai lingkup tanggung jawab.\nMemiliki hak akses atas aplikasi Digital Platform Strategy.\nMenetapkan sumber data yang digunakan dalam pekerjaan.\nMenetapkan metodologi kerja sesuai standar unit.\nMengembangkan kompetensi diri untuk mendukung pencapaian kinerja.
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response:
        job_authorities = response.strip()

        job_authorities = job_authorities.replace("- ", "• ")
        job_authorities = job_authorities.replace("'", "").replace("[", "").replace("]", "")

        return job_authorities
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."
