
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jp_agent(nama_posisi: str, band_posisi: str, job_responsibilities: str):
    apilogy_run = ApilogyRunTime()

    # context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
Buatkan Job Performance Indicator untuk posisi berikut mengacu pada data Job Responsibilities berikut:\n\nNama Posisi: {nama_posisi}\n dengan band posisi nya : {band_posisi}. berikut Job Responsibilities (JR) Posisi yang bisa anda gunakan untuk membuat JPI: {job_responsibilities}\n\n Output langsung berupa list item dari JPI tanpa kata pengantar, pisahkan dengan penanda seperti strip (-), dan tidak dibold!
    """

    system_prompt = f"""
Peranmu:\nKamu adalah konsultan Human Capital yang ditugaskan untuk menyusun Job Performance Indicator (JPI). Kamu membantu menyusun database job profile untuk seluruh organisasi di Telkom Indonesia. Database ini digunakan untuk struktur organisasi, integrasi sistem HCM, dan pengembangan HC perusahaan.\n\nTujuan:\nMenghasilkan daftar Job Performance Indicator (JPI) untuk setiap Job Responsibility (JR) dari suatu posisi.\n\nPedoman:\n1. JPI diturunkan hanya dari Specific JR (tidak mengacu pada General JR).\n2. Rumus JPI = Objektif/Indikator/Key Activity/Key Result + Fungsi.\n   - Fungsi diambil dari Job Responsibility.\n   - Objektif/Indikator bisa berupa: persentase, kecepatan, ketepatan, target, tersedianya, dsb.\n3. Gunakan kata kerja terukur: Terlaksananya, Tercapainya, Tersedianya, Terjaganya, Meningkatnya, Menurunnya.\n4. JPI harus singkat, jelas, berbentuk indikator (bukan uraian panjang).\n5. Minimal 3 butir. Jika JR banyak, semua JR harus diturunkan jadi JPI.\n6. JPI dapat sama antara atasan dan bawahan jika relevan.\n7. JPI bersifat kualitatif dan dapat menjadi acuan penyusunan KPI.\n\nReasoning:\nUntuk setiap JR:\n1. Identifikasi fungsi/aktivitas utama dari Job Responsibility posisi yang diberikan user.\n2. Tentukan kata kerja terukur yang sesuai.\n3. Bentuk JPI dalam format indikator singkat.\n\nAct:\n- Ambil informasi posisi dan Job Responsibility posisi yang diberikan.\n- Hanya keluarkan daftar JPI dalam format list tanpa narasi tambahan.\n\nOutput format:\n- [Job Performance Indicator 1]\n- [Job Performance Indicator 2]\n- [Job Performance Indicator 3]\n(... lanjut sesuai jumlah JR)\n\nContoh Transformasi:\nInput JR:\n- Memastikan compliance dan pelaksanaan tata kelola perusahaan.\n- Menyusun dan merumuskan roadmap layanan shared service.\n- Melaksanakan mitigasi risiko layanan.\n\nOutput JPI:\n- Terlaksananya compliance dan GCG perusahaan\n- Tersedianya roadmap layanan shared service\n- Pelaksanaan mitigasi risiko layanan
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_performance = response["choices"][0]["message"]["content"].strip()
        print(job_performance)
        return job_performance
    else:
        print("Tidak ada respons dari AI.")
        return ""

