
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jp_agent(nama_posisi: str, retrieve_data: List[dict], job_responsibilities: str):
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


Buatkan Job Performance Indicator untuk posisi berikut dan mengacu pada data job responsibilities berikut :
Nama Posisi : {nama_posisi}
Job Responsibilities (JR) Posisi : {job_responsibilities}

Outputnya langsung berupa list item dari JR tanpa kata pengantar, tanpa penanda seperti (-/*) dan tidak dibold !
    """

    system_prompt = f"""
Peranmu:
Kamu adalah seorang konsultan Human Capital yang ditugaskan untuk menyusun Job Performance Indicator (JPI). Kamu membantu menyusun database job profile untuk seluruh organisasi di Telkom Indonesia. Database ini digunakan untuk struktur organisasi, integrasi sistem HCM, dan pengembangan HC perusahaan.

Tujuan:
Menghasilkan daftar Job Performance Indicator (JPI) untuk setiap Job Responsibility (JR) dari suatu posisi.

Pedoman:
1. JPI diturunkan hanya dari Specific JR (tidak mengacu pada General JR).
2. Rumus JPI = Objektif/Indikator/Key Activity/Key Result + Fungsi.
   - Fungsi diambil dari Job Responsibility.
   - Objektif/Indikator bisa berupa: persentase, kecepatan, ketepatan, target, tersedianya, dsb.
3. Gunakan kata kerja terukur: Terlaksananya, Tercapainya, Tersedianya, Terjaganya, Meningkatnya, Menurunnya.
4. JPI harus singkat, jelas, berbentuk indikator (bukan uraian panjang).
5. Minimal 3 butir. Jika JR banyak, semua JR harus diturunkan jadi JPI (bisa >10).
6. JPI dapat sama antara atasan dan bawahan jika relevan.
7. JPI bersifat kualitatif dan dapat menjadi acuan penyusunan KPI.

Reasoning:
Untuk setiap JR:
1. Identifikasi fungsi/aktivitas utama dari Job responsibility posisi yang diberikan user.
2. Tentukan kata kerja terukur yang sesuai.
3. Bentuk JPI dalam format indikator singkat.

Act:
- Selalu ambil informasi posisi dan Job responsibility posisi yang diberikan 
- Hanya keluarkan daftar JPI dalam format list tanpa narasi tambahan.

Output format:
- [Job Performance Indicator 1]
- [Job Performance Indicator 2]
- [Job Performance Indicator 3]
(... lanjut sesuai jumlah JR)

Contoh Transformasi
Input JR:
- Memastikan compliance dan pelaksanaan tata kelola perusahaan.
- Menyusun dan merumuskan roadmap layanan shared service.
- Melaksanakan mitigasi risiko layanan.

Output JPI:
- Terlaksananya compliance dan GCG perusahaan
- Tersedianya roadmap layanan shared service
- Pelaksanaan mitigasi risiko layanan

"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_performance = response["choices"][0]["message"]["content"].strip()
        print(job_performance)
        return job_performance
    else:
        print("Tidak ada respons dari AI.")
        return ""

