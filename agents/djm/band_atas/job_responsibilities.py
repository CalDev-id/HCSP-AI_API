
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jr_agent(nama_posisi: str, band_posisi: str, retrieve_data: str):
    apilogy_run = ApilogyRunTime()

    context_text = retrieve_data if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
Buatkan Job Responsibilities untuk posisi berikut tanpa diubah atau ditambah isi dari aktivitas utamanya. Nama Posisi: {nama_posisi} Band Posisi: {band_posisi}. Output langsung berupa list item dari JR, output tanpa kata pengantar, antar list item dipisahkan dengan penanda strip (-), dan tidak dibold. Berikut adalah context yang dapat anda gunakan untuk membentuk JR dari aktivitas utamanya bukan kewenangannya : {context_text}   
"""

    system_prompt = f"""
Kamu adalah konsultan Human Capital berpengalaman. Tugasmu adalah membantu membuat Job Responsibilities (JR). Reasoning (Langkah Berpikir): (1. Ambil konteks → penting, Tidak semua point dalam chunk pasal perlu dipakai, cukup gunakan dan pahami chunk yang sumber pasalnya sesuai dengan nama fungsi posisi untuk memahami fungsi, unit kerja, dan aktivitas utamanya. (2. Cari di context chunk dengan sumber pasal yang sesuai nama posisi semua poin-poin aktivitas utama posisi dan ingat (bukan wewenang atau kewenangan). (3. cukup ambil dari aktivitas utamanya saja tidak perlu ambil poin posisi tersebut berinteraksi dengan siapa dan tidak perlu ambil kewenangannya. (4. Buat JR dengan rumus: - Posisi Band I atau II → salin langsung semua JANGAN DITAMBAH ATAU MENGUBAH dari aktivitas utama posisi tersebut dari context yang diberikan user, TANPA MENAMBAH DAN DIUBAH - Dari informasi context chunk yang diberikan tersebut, cari aktivitas utama yang dijalankan posisi tersebut di dalam chunk pasal BUKAN WEWENANG atau poin relasi interaksi !. Act: - Buat Job Responsibilities dengan menyalin semua aktivitas utama untuk masing-masing posisi. Untuk Band I dan II WAJIB ambil dan salin langsung dari aktivitas utama posisi tersebut dari context yang diberikan user TANPA BERKHAYAL UNTUK MENAMBAH ATAU MENGUBAH NARASINYA, disalin SEMUA dan tidak diubah atau ditambah tambah. - JR Deputy sama dengan JR atasan Band I-nya dalam chunk context (misal SGM, EVP, dll) disesuaikan dengan nama fungsinya.  terakhir, Susun hasil → gabungkan SEMUA Specific JR sesuai band posisi dan nama posisinya. Act (Output yang Harus Dihasilkan): Hasilkan daftar Job Responsibilities dalam format bullet point: - [Specific Responsibility 1] - [Specific Responsibility 2] - [Specific Responsibility 3]. Contoh Alur Singkat: - SGM (Band I/II) → JR langsung COPY semua TANPA DIUBAH ATAU DITAMBAH NARASINYA dari aktivitas posisi yang diambil dari context yang diberikan user berupa informasi isi pasal. - SM (Band II) → JR langsung COPY semua TANPA DIUBAH ATAU DITAMBAH NARASINYA dari aktivitas utama posisi yang diambil dari context yang diberikan user berupa chunk dengan sumber pasal yang sesuai dengan nama posisinya. Pedoman Kata Kerja (per Band): - BP 1 & 2 Managerial → Menyetujui, Mengarahkan, Merencanakan, Mengembangkan, Menentukan, Memberi otorisasi

"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response:
        job_responsibilities = response.strip()
        
        job_responsibilities = job_responsibilities.replace("- ", "• ")
        job_responsibilities = job_responsibilities.replace("'", "").replace("[", "").replace("]", "")
        
        return job_responsibilities
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."