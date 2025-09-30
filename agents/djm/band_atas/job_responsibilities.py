
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jr_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[str]):
    apilogy_run = ApilogyRunTime()

    context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
Buatkan Job Responsibilities untuk posisi berikut:\\n\\n Nama Posisi: {nama_posisi} \\n\\n dengan band posisi nya : {band_posisi}. Perlu diingat singkatan berikut, perluas singkatan yang ada di nama posisi diikuti dengan nama fungsinya:\\n1. SGM = senior general manager + [nama fungsi]\\n2. SM = senior manager + [nama fungsi]\\n\\nOutput langsung berupa list item dari JR tanpa kata pengantar, pisahkan dengan penanda seperti strip (-) , dan tidak dibold!\\n\\n Berikut adalah context yang dapat anda gunakan untuk membentuk JR dari aktivitas utamanya : {context_text}
    """

    system_prompt = f"""
Kamu adalah konsultan Human Capital berpengalaman. Tugasmu adalah membantu membuat Job Responsibilities (JR).\\n\\nReasoning (Langkah Berpikir):\\n1. Ambil konteks → gunakan get_context untuk memahami posisi, unit kerja, dan aktivitas utama posisi tersebut. Cari dalam tools context chunk berupa aktivitas utama posisi/atasan posisi yang sesuai dengan nama fungsi (bukan wewenang). Wajib gunakan format pencarian nama posisi lengkap beserta singkatannya, contoh: \\"aktivitas utama senior general manager (sgm)\\".\\n\\n2. Tentukan lingkup peran → pahami aktivitas inti, produk/fungsi yang ditangani, dan relasi antar unit.\\n\\n3. Buat JR dengan rumus:\\n   - Posisi band I atau II → ambil langsung dari aktivitas utama posisi tersebut yang diambil dari context yang diberikan user, disalin SEMUA dan tidak diubah.\\n\\n4. Validasi prinsip JR → pastikan JR:\\n   - Faktual, spesifik, aktual, relatif tetap.\\n   - Mencerminkan hasil utama, bukan sekadar proses.\\n   - Terukur keberhasilannya.\\n\\n5. Susun hasil → gabungkan SEMUA Specific JR sesuai band posisi dan nama posisinya.\\n\\nAct (Output yang Harus Dihasilkan):\\nHasilkan daftar Job Responsibilities dalam format bullet point:\\n\\n- Specific JR (berdasarkan band/posisi & kata kerja pedoman):\\n  [Specific Responsibility 1]\\n  [Specific Responsibility 2]\\n  [Specific Responsibility 3]\\n  … (sesuai kebutuhan)\\n\\nContoh Alur (Singkat):\\n- SGM (Band I/II) → JR langsung COPY semua dari aktivitas posisi yang diambil dari context yang diberikan user berupa chunk .\\n- SM (Band II) → JR langsung context semua dari aktivitas posisi yang diambil dari context yang diberikan user berupa chunk
"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_responsibilities = response["choices"][0]["message"]["content"].strip()
        return job_responsibilities
    else:
        print("Tidak ada respons dari AI.")
        return ""
