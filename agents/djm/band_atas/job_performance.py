
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jp_agent(nama_posisi: str, job_responsibilities: str):
    apilogy_run = ApilogyRunTime()

    user_prompt = f"""
Buatkan Job Performance Indicator untuk posisi berikut mengacu pada data Job Responsibilities berikut: Nama Posisi: {nama_posisi} . Berikut Job Responsibilities (JR) posisi yang bisa anda gunakan untuk membuat JPI dari posisi itu: {job_responsibilities} Output langsung berupa list item dari JPI, output tanpa kata pengantar, antar list item dipisahkan dengan penanda strip (-), dan tidak dibold !
    """

    system_prompt = f"""
Peranmu: Konsultan HC penyusun JPI dari JR. Tujuan: Ubah setiap JR jadi JPI. Aturan: (1) 1 JR = 1 JPI. (2) Rumus JPI = Kata kerja terukur + fungsi JR. Kata kerja terukur: [memberikan/menyusun/menetapkan/memastikan] → diubah menjadi [Tersedianya]; [melakukan/mengelola] → diubah menjadi [Terlaksananya] atau bisa juga [Tercapainya/Meningkatnya/Menurunnya]. (3) JPI singkat, jelas, indikator. (4) Bisa sama untuk atasan/bawahan jika relevan. Act: Ambil setiap JR, tentukan kata kerja sesuai aturan, bentuk list JPI tanpa narasi. Output format: - [JPI 1] - [JPI 2] - [JPI 3]. Contoh => JR : Menetapkan kebijakan evaluasi organisasi → JPI : Tersedianya kebijakan evaluasi organisasi; JR : Mengelola program evaluasi berkala → JPI : Terlaksananya program evaluasi berkala.
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response:
        job_performance = response.strip()
        
        job_performance = job_performance.replace("- ", "• ")
        job_performance = job_performance.replace("'", "").replace("[", "").replace("]", "")
        
        return job_performance
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."