
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jp_agent(nama_posisi: str, band_posisi: str, job_responsibilities: str):
    apilogy_run = ApilogyRunTime()

    # context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
Buatkan Job Performance Indicator untuk posisi berikut dan mengacu pada data job responsibilities berikut:\n Nama Posisi :{nama_posisi}. dan \n berikut Job Responsibilities (JR) Posisi tersebut : {job_responsibilities} \n\n Outputnya langsung berupa list item dari JPI tanpa kata pengantar, dan pisahkan dengan penanda seperti strip (-) serta tidak dibold!
     """

    system_prompt = f"""
Peranmu:\nKamu adalah seorang konsultan Human Capital yang ditugaskan untuk menyusun Job Performance Indicator (JPI). Kamu membantu menyusun database job profile untuk seluruh organisasi di Telkom Indonesia.\n\nTujuan:\nMenghasilkan daftar Job Performance Indicator (JPI) untuk setiap Job Responsibility (JR) dari suatu posisi.\n\nPedoman:\n1. JPI diturunkan hanya dari Specific JR (tidak mengacu pada General JR).\n2. Rumus JPI = Objektif/Indikator/Key Activity/Key Result + Fungsi.\n   - Fungsi diambil dari Job Responsibility.\n   - Objektif/Indikator bisa berupa: persentase, kecepatan, ketepatan, target, tersedianya, dsb.\n3. Gunakan kata kerja terukur: Terlaksananya, Tercapainya, Tersedianya, Terjaganya, Meningkatnya, Menurunnya.\n4. JPI harus singkat, jelas, berbentuk indikator.\n5. Minimal 3 butir. Jika JR banyak, semua JR harus diturunkan jadi JPI.\n6. JPI dapat sama antara atasan dan bawahan jika relevan.\n7. JPI bersifat kualitatif dan dapat menjadi acuan penyusunan KPI.\n\nReasoning:\nUntuk setiap JR:\n1. Identifikasi fungsi utama dari JR posisi.\n2. Tentukan kata kerja terukur yang sesuai.\n3. Bentuk JPI dalam format indikator singkat.\n\nAct:\n- Ambil informasi posisi dan Job Responsibility yang diberikan.\n- Keluarkan daftar JPI dalam format list tanpa narasi tambahan.\n\nOutput format:\n[Job Performance Indicator 1]\n[Job Performance Indicator 2]\n[Job Performance Indicator 3]\n(... lanjut sesuai jumlah JR)\n\nContoh:\nInput JR:\nMemastikan compliance dan pelaksanaan tata kelola perusahaan.\nMenyusun dan merumuskan roadmap layanan shared service.\nMelaksanakan mitigasi risiko layanan.\n\nOutput JPI:\nTerlaksananya compliance dan GCG perusahaan\nTersedianya roadmap layanan shared service\nPelaksanaan mitigasi risiko layanan
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_performance = response["choices"][0]["message"]["content"].strip()
        
        # Bersihkan teks
        job_performance = job_performance.replace("- ", "• ")
        job_performance = job_performance.replace("'", "").replace("[", "").replace("]", "")
        
        return job_performance
    else:
        print("Tidak ada respons dari AI.")
        return ""

