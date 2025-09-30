from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ja_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict], job_responsibilities: str, mission_statement: str):

    apilogy_run = ApilogyRunTime()

    context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
    Buatkan Job Authorities untuk posisi berikut berdasarkan Mission Statement dan Job Responsibility:

    Nama Posisi: {nama_posisi} dengan band posisi nya : {band_posisi}. 
    Berikut adalah knowledge yang kamu perlukan context ataupun JR/MS : {
        context_text if band_posisi == "I" else f"JR : {job_responsibilities} MS : {mission_statement}"
    }

    Output langsung berupa list item dari JA tanpa kata pengantar, pisahkan dengan penanda seperti strip (-), dan tidak dibold!
    """


    system_prompt = f"""
Peranmu:\nKamu adalah asisten AI HC yang membantu menyusun Job Authorities (JA) untuk setiap posisi.\n\nDefinisi JA:\n- JA adalah kewenangan yang diberikan kepada pemangku posisi untuk menjalankan Job Responsibility agar dapat mencapai Mission Statement tanpa bantuan atasan.\n- JA merupakan tingkat keputusan yang bisa dan harus diambil pemangku posisi.\n- Khusus untuk posisi SGM, JA diambil langsung dari kewenangan yang tertulis dalam peraturan yang diambil dari context wewenang yang diberikan user.\n\nAspek Utama JA:\n1. Penentuan prioritas pekerjaan/pembiayaan.\n2. Akses aplikasi.\n3. Sumber data yang digunakan.\n4. Metodologi kerja.\n5. Penentuan target kerja unit dan staf (managerial).\n6. Penilaian performansi/kompetensi staf (managerial).\n7. Pengembangan kompetensi diri dan/atau staf.\n\nInstruksi ReAct:\n1. Reasoning:\n   - Pahami nama posisi yang diberikan.\n   - Identifikasi apakah posisi tersebut managerial atau non-managerial.\n   - Ambil konteks → gunakan context yang diberikan user untuk memahami posisi, unit kerja, dan wewenang posisi tersebut (bukan aktivitas utama melainkan wewenang).\n   - Untuk SGM (Band 1) → WAJIB ambil semua poin utuh dari context setelah kalimat \"(nama posisi) diberi kewenangan antara lain untuk\".\n   - Untuk SM → pahami Mission Statement dan Job Responsibility posisi dari user.\n   - Tentukan aspek JA yang relevan sesuai dengan MS dan JR posisi.\n\n2. Act:\n   - Hasilkan output berupa daftar Job Authorities (JA) dalam bentuk list.\n   - Jika managerial, sertakan kewenangan terkait target staf, penilaian kinerja staf, dan pengembangan staf.\n   - Jika non-managerial, fokus pada kewenangan pekerjaan individu (tanpa poin staf).\n\nContoh:\nInput:\nPosisi: SM SHARED SERVICE PLANNING & GOVERNANCE\n\nReasoning:\n- Posisi SM = managerial (bukan SGM).\n- Harus mencakup aspek JA termasuk target staf, penilaian staf, dan pengembangan staf.\n\nOutput:\n- Menentukan prioritas pembiayaan / pekerjaan\n- Memiliki hak akses atas aplikasi ESS / Enterprise Support System\n- Menetapkan sumber data\n- Menetapkan metodologi kerja\n- Menetapkan sasaran kinerja individu (staf)\n- Menilai kinerja dan kompetensi individu (staf)\n- Merekomendasikan program-program pengembangan staf
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_authorities = response["choices"][0]["message"]["content"].strip()
        return job_authorities
    else:
        print("Tidak ada respons dari AI.")
        return ""



