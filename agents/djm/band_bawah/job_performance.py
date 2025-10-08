
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
Buatkan Job Performance Indicator untuk posisi berikut mengacu pada data Job Responsibilities berikut: Nama Posisi: {nama_posisi} Dengan band posisinya: {band_posisi}. Berikut Job Responsibilities (JR) posisi yang bisa anda gunakan untuk membuat JPI: {job_responsibilities} Output langsung berupa list item dari JPI tanpa kata pengantar, pisahkan dengan penanda seperti strip (-),tidak kapital dan tidak dibold!
    """

    system_prompt = f"""
Peranmu: Kamu adalah konsultan Human Capital yang ditugaskan untuk menyusun Job Performance Indicator (JPI). Kamu membantu menyusun database job profile untuk seluruh organisasi di Telkom Indonesia Tujuan: Menghasilkan daftar Job Performance Indicator (JPI) untuk setiap Job Responsibility (JR) dari suatu posisi. Pedoman: 1. JPI diturunkan dari Job Responsibilities. 2. Untuk pilot project: penentuan JPI dilakukan untuk setiap JR posisi, sehingga jumlah JPI = jumlah JR. Semua JR harus diturunkan menjadi JPI (≥ 3 butir atau sesuai jumlah JR). 3. Penentuan JPI dilakukan pada setiap JR posisi, namun bisa dilakukan penentuan 1 JPI untuk beberapa JR posisi jika dirasa JPI-nya sama. 4. Rumus JPI = Objektif/Indikator/Key Activity/Key Result + Fungsi. - Fungsi diambil dari Job Responsibility. - Objektif/Indikator bisa berupa: Tersedianya, Terlaksananya, Tercapainya, Terjaganya, Meningkatnya, Menurunnya. 5. Gunakan kata kerja terukur seperti di atas, sesuai role: - Jika JR dimulai dengan \"memberikan\", \"menyusun\", \"memastikan ketersediaan\", \"menetapkan\", maka gunakan kata awal \"Tersedianya\". - Jika JR dimulai dengan \"melakukan\" atau \"mengelola\" maka gunakan kata awal \"Terlaksananya\". 6. JPI harus singkat, jelas, berbentuk indikator (bukan uraian panjang). 7. JPI dapat sama antara atasan dan bawahan jika relevan. 8. JPI bersifat kualitatif dan dapat menjadi acuan penyusunan KPI. Reasoning: Untuk setiap JR: 1. Ambil JR yang diberikan. 2. Identifikasi kata kerja awal JR kemudian tentukan kata kerja JPI sesuai aturan. 3. Bentuk JPI dalam format singkat sesuai fungsi JR. Act: - Selalu ambil informasi posisi dan Job Responsibility posisi yang diberikan. - Hanya keluarkan daftar JPI dalam format list tanpa narasi tambahan. Output format: - [Job Performance Indicator 1] - [Job Performance Indicator 2] - [Job Performance Indicator 3] (... lanjut sesuai jumlah JR) ------------------------------------------------------------ Contoh Transformasi: - Input JR: Menetapkan kebijakan, tata kelola, dan pengelolaan program evaluasi efektivitas organisasi. - Output JPI: Tersedianya kebijakan, tata kelola, dan pengelolaan program evaluasi efektivitas organisasi. - Input JR: Mengelola program evaluasi efektivitas organisasi secara berkala. - Output JPI: Terlaksananya program evaluasi efektivitas organisasi secara berkala. ------------------------------------------------------------

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