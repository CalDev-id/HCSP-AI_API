
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jr_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict]):
    apilogy_run = ApilogyRunTime()

    if not retrieve_data:
      context_text = "Tidak ada konteks pasal relevan."
    else:
      context_parts = []
      for record in retrieve_data:
          job_responsibilities = record.get("job_responsibilities", "")
          context_parts.append(f"Job Responsibilities: {job_responsibilities}\n\n")
        
      context_text = "\n\n".join(context_parts)

    user_prompt = f"""
Buatkan Job Responsibilities untuk posisi berikut:\n\nNama Posisi : {nama_posisi}  dengan band posisinya yaitu : {band_posisi}. dan berikut adalah list tugas atasan dari posisi tersebut yang kamu bisa tentukan sesuai nama fungsi posisi tsb dan kamu gunakan : {context_text}. Outputnya langsung berupa list item dari JR tanpa kata pengantar dan pisahkan dengan penanda seperti strip (-) serta tidak dibold!
    """

    system_prompt = f"""
Tugasmu adalah membantu membuat Job Responsibilities (JR).\n\n=====================================================\nReasoning (Langkah Berpikir)\n\n1. Buat JR dengan rumus:\n   JR = Kata Kerja + Fungsi/Aktivitas/Produk\n   - Gunakan kata kerja sesuai pedoman band/posisi.\n2. Pembuatan JR diturunkan dari JR ATASANNYA:\n   - Posisi MGR atau OFF → WAJIB diambil dari JR atasannya yang diberikan oleh user (MGR dari SM, OFF dari MGR).\n   - Untuk MGR atau OFF, penurunan JR dari atasannya disesuaikan antara nama fungsi dari posisinya dengan tiap tugas dari atasannya yang bersesuaian. contoh -> nama posisi = jabatan + [nama fungsi]. \n3. Susun hasil → SEMUA Specific JR sesuai band posisi dan posisinya.\n\n=====================================================\nAct (Output yang Harus Dihasilkan)\nHasilkan daftar Job Responsibilities dalam format list:\n\nSpecific JR (berdasarkan band/posisi & kata kerja pedoman):\n[Specific Responsibility 1]\n[Specific Responsibility 2]\n[Specific Responsibility 3]\n… (sesuai kebutuhan)\n\n=====================================================\nPedoman Kata Kerja (per Band)\n\nBP 3 Managerial → Mencapai, Memastikan, Mengevaluasi, Mengidentifikasi, Memantau, Meningkatkan, dll.\nBP 3 Non-Managerial & Officer (BP 4/6) → Membandingkan, Mengoperasikan, Melaksanakan, Menyajikan, Menghasilkan, Memberitahukan, dll.\n\n=====================================================\nContoh Alur\n\n MGR (Band III) → ambil dari tugas atasan yang diberikan lalu, strukturisasi sesuai nama fungsi → diturunkan ke Officer.\n Officer (Band IV/VI) → ambil dari tugas atasan yang diberikan lalu, strukturisasi sesuai kata kerja & nama fungsi. Jika beberapa officer punya fungsi sama, JR bisa sama.\n\n=====================================================

"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_responsibilities = response["choices"][0]["message"]["content"].strip()
        print(job_responsibilities)
        return job_responsibilities
    else:
        print("Tidak ada respons dari AI.")
        return ""
