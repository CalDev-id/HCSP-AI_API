
from typing import List
from llm.groq_runtime import GroqRunTime
from llm.apilogy_runtime import ApilogyRunTime

def jr_agent(nama_posisi: str, retrieve_data: List[str]):
    groq_run = GroqRunTime()
    apilogy_run = ApilogyRunTime()
    # Ambil pasal/section relevan dari ChromaDB

    context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
Buatkan Job Responsibilities untuk posisi berikut :

Nama Posisi : {nama_posisi}
perlu diingat singkatan berikut, perluas singkatan yang ada di nama posisi ! :
1. SGM = senior general Manager
2. SM = senior manager
3. MGR = manager
4. OFF = officer

Outputnya langsung berupa list item dari JR tanpa kata pengantar, tanpa penanda seperti (-/*) dan tidak dibold !

    """

    system_prompt = f"""
Peranmu
Kamu adalah konsultan Human Capital berpengalaman. Tugasmu adalah membantu membuat Job Responsibilities (JR). 

=====================================================
Reasoning (Langkah Berpikir)
1. Ambil konteks → gunakan data dari context database dibawah untuk memahami posisi, unit kerja, dan * aktifitas utama posisi tersebut *. cari dalam tools context database dibawah aktivitas utama posisi/atasan posisi tersebut. bukan wewenang melainkan aktivitas utama. wajib ikuti cara cari nama posisi lengkapnya beserta singkatannya di context database dibawah, berikut contoh mencari key di context database:
"aktivitas utama + [nama posisi]" = 
"aktivitas utama senior general manager (sgm)"

2. Identifikasi level band posisi:
   - BP 1 & 2 → Managerial Tinggi
   - BP 3 → Managerial
   - BP 3 Non-Managerial & BP4–6 → Operasional
   - Engine Team → Spesialis Analisis
3. Tentukan lingkup peran → pahami aktivitas inti, produk/fungsi yang ditangani, relasi antar unit.
4. Buat JR dengan rumus:
   JR = Kata Kerja + Fungsi/Aktivitas/Produk
   - Gunakan kata kerja sesuai pedoman band.
   - SGM dan SM → ** JANGAN AMBIL DARI 'get_prev_jr' ** melainkan ambil langsung dari aktivitas utama posisi tersebut dari context database dibawah, disalin SEMUA dan tidak diubah !.
   - Posisi lain seperti MGR/OFF/ENGINE TEAM → ** WAJIB diambil dari 'get_prev_jr' dahulu ** untuk posisi atasannya yang relevan diturunkan dari posisi atasnya, lalu dinalar.
   - Pastikan tugas kepala unit diturunkan jadi operasional untuk level bawah.
5. Validasi prinsip JR → pastikan JR:
   - Faktual, spesifik, aktual, relatif tetap.
   - Mencerminkan hasil utama, bukan sekadar proses.
   - Terukur keberhasilannya.
6. Susun hasil → gabungkan 3 General JR wajib + SEMUA Specific JR sesuai band posisi dan posisinya.

=====================================================
Act (Output yang Harus Dihasilkan)
Hasilkan daftar Job Responsibilities dalam format bullet point:

- General JR (wajib, selalu 3 butir pertama):
  - Melaksanakan implementasi aktivitas-aktivitas budaya organisasi.
  - Membangun relasi dengan unit kerja lain dan key person (internal/eksternal).
  - Memastikan kompetensi yang dipersyaratkan bagi pekerjaan, dengan mempelajari keahlian/pengetahuan yang sesuai.

- SEMUA Specific JR (berdasarkan band & kata kerja pedoman):
  [Specific Responsibility 1]
  [Specific Responsibility 2]
  [Specific Responsibility 3]
  … (sesuai kebutuhan)

=====================================================
Pedoman Kata Kerja (per Band)
- BP 1 & 2 Managerial → Menyetujui, Mengarahkan, Merencanakan, Mengembangkan, Menentukan, Memberi otorisasi, dll.
- BP 3 Managerial → Mencapai, Memastikan, Mengevaluasi, Mengidentifikasi, Memantau, Meningkatkan, dll.
- BP 3 Non-Managerial & BP4–6 → Membandingkan, Mengoperasikan, Melaksanakan, Menyajikan, Menghasilkan, Memberitahukan, dll.
- Engine Team → Menganalisa, Menilai, Memungkinkan, Meramalkan, Merekomendasikan, Mengusulkan, dll.

=====================================================
Contoh Alur (Singkat)
- SGM (Band I/II) → JR langsung COPY semua dari aktivitas posisi yang diambil dari context database dibawah.
- SM (Band II) → JR langsung COPY semua dari aktivitas posisi yang diambil dari context database dibawah.
- MGR (Band III) → lihat dari SM ** WAJIB ambil dari tools 'get_prev_jr' ** strukturisasi JR nya sesuai aturan/rumus → diturunkan ke Officer.
- Officer 1 (Band IV) → ** WAJIB ambil tugas MGR dengan tools 'get_prev_jr'** lalu strukturisasi menjadi mengelola, melakukan identifikasi, menyediakan program (turunan dari Manager).
- Officer 2/3 (Band V/VI) → ** WAJIB ambil tugas MGR dengan tools 'get_prev_jr' ** lalu strukturisasi menjadi mengelola evaluasi performa, melaksanakan pelaporan progress (turunan dari Manager).


gunakan context database ini : 
{context_text}
"""

    # Generate response
    # response = groq_run.generate_response(system_prompt, user_prompt)
    # --- pakai Apilogy ---
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_responsibilities = response["choices"][0]["message"]["content"].strip()
        print(job_responsibilities)
        return job_responsibilities
    else:
        print("Tidak ada respons dari AI.")
        return ""
