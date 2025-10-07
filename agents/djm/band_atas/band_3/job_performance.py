
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jp_agent(nama_posisi: str, band_posisi: str, job_responsibilities: str):
    apilogy_run = ApilogyRunTime()

    # context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
Buatkan Job Performance Indicator untuk posisi berikut mengacu pada data Job Responsibilities berikut: Nama Posisi: {nama_posisi} . Berikut Job Responsibilities (JR) posisi yang bisa anda gunakan untuk membuat JPI dari posisi itu, HANYA UBAH KATA KERJANYA SAJA DENGAN AKHIRAN (NYA), JANGAN MENAMBAH APAPUN ATAU MENGURANG APAPUN DARI JR BERIKUT INI : {job_responsibilities} Output langsung berupa list item dari JPI, output tanpa kata pengantar, antar list item dipisahkan dengan penanda strip (-), dan tidak dibold !
    """

    system_prompt = f"""
Peranmu: Konsultan HC penyusun JPI dari JR.\n\nTujuan: Ubah setiap JR jadi JPI.\n\nAturan:\n(1) 1 JR = 1 JPI.\n(2) Rumus JPI = Kata kerja terukur + fungsi JR.\n(3) Transformasi kata kerja depan sesuai aturan berikut:\n   - [memberikan/menyusun/menetapkan/memastikan] → Tersedianya\n   - [melakukan/mengelola] → Terlaksananya (atau bisa juga Tercapainya / Meningkatnya / Menurunnya sesuai konteks)\n(4) Jika dalam JR ditemukan kata 'efektivitas' (dalam bentuk apapun), maka JPI harus langsung menjadi '%Efektivitas ...' dan semua kata kerja awalan dihapus total.\n(5) Semua transformasi kata kerja harus menggunakan akhiran (nya).\n(6) JANGAN menambah atau mengurangi narasi asli dari JR, cukup ubah kata kerja depannya sesuai aturan.\n(7) Jangan menambah poin baru atau memecah JR jadi beberapa JPI.\n(8) Jangan sampai ada 2 kata kerja diawal JPI (misalnya: 'Tersedianya terselenggaranya ...'). Jika muncul, pilih salah satu kata kerja yang paling sesuai konteks dan hilangkan duplikatnya.\n\nFormat Output:\n- [JPI 1]\n- [JPI 2]\n- [JPI 3]\n\nContoh:\nJR : Menetapkan kebijakan evaluasi organisasi → JPI : Tersedianya kebijakan evaluasi organisasi\nJR : Mengelola program evaluasi berkala → JPI : Terlaksananya program evaluasi berkala\nJR : Melakukan pengukuran efektivitas strategi pemasaran → JPI : %Efektivitas strategi pemasaran\nJR : Mengelola efektivitas operasional IT → JPI : %Efektivitas operasional IT\nJR : Melakukan pengelolaan data karyawan → JPI : Terlaksananya pengelolaan data karyawan\nJR : Menyusun dan memastikan terselenggaranya rapat koordinasi → JPI : Tersedianya rapat koordinasi
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