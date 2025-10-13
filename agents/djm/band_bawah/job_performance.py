
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jp_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict], job_responsibilities: str):
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
Buatkan Job Performance Indicator untuk posisi berikut mengacu pada data Job Responsibilities berikut: Nama Posisi: {nama_posisi}. Berikut Job Responsibilities (JR) posisi yang bisa anda gunakan untuk membuat JPI. HANYA UBAH KATA KERJANYA SAJA DENGAN AKHIRAN (NYA), JANGAN MENAMBAH APAPUN ATAU MENGURANG APAPUN DARI JR BERIKUT INI : {job_responsibilities} Output langsung berupa list item dari JPI tanpa kata pengantar, pisahkan dengan penanda seperti bullet (•),tidak kapital dan tidak dibold!
    """

    system_prompt = f"""
Peranmu: Konsultan HC penyusun JPI dari JR. Tujuan: Ubah setiap JR jadi JPI. Aturan: (1) 1 JR = 1 JPI. jangan mengulang ulang terus jpi yang sama, sehingga jumlah point JPI = point Jumlah JR, jika jumlah JPI lebih banyak dari JR yang diberikan, maka jawaban anda salah (2) Rumus JPI = Kata kerja terukur + fungsi JR. (3) Transformasi kata kerja depan sesuai aturan berikut: - [memberikan, menyusun, menetapkan, memastikan] → Tersedianya - [melakukan, mengelola] → Terlaksananya (atau bisa juga Tercapainya / Meningkatnya / Menurunnya sesuai konteks) (4) Jika dalam JR ditemukan kata efektivitas (dalam bentuk apapun), maka JPI harus langsung menjadi %Efektivitas ... dan semua kata kerja awalan dihapus total. (5) Semua transformasi kata kerja harus menggunakan akhiran nya. (6) Jangan menambah atau mengurangi narasi asli dari JR, cukup ubah kata kerja depannya sesuai aturan. (7) Jangan menambah poin baru atau memecah JR jadi beberapa JPI. (8) Jangan sampai ada dua kata kerja di awal JPI (misalnya: Tersedianya terselenggaranya ...). Jika muncul, pilih salah satu kata kerja yang paling sesuai konteks dan hilangkan duplikatnya. Format Output:  • [JPI 1] • [JPI 2] • [JPI 3] Contoh: JR: Menetapkan kebijakan evaluasi organisasi → JPI: Tersedianya kebijakan evaluasi organisasi JR: Mengelola program evaluasi berkala → JPI: Terlaksananya program evaluasi berkala JR: Melakukan pengukuran efektivitas strategi pemasaran → JPI: %Efektivitas strategi pemasaran JR: Mengelola efektivitas operasional IT → JPI: %Efektivitas operasional IT JR: Melakukan pengelolaan data karyawan → JPI: Terlaksananya pengelolaan data karyawan JR: Menyusun dan memastikan terselenggaranya rapat koordinasi → JPI: Tersedianya rapat koordinasi
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