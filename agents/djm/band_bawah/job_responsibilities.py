from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jr_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[dict], field_name: str = "job_responsibilities"):
    """
    Generate Job Responsibilities berdasarkan data atasan yang relevan.
    - field_name bisa diubah untuk memilih field sumber (misal: 'job_responsibilities', 'mission_statement', dll)
    """

    apilogy_run = ApilogyRunTime()

    if not retrieve_data:
        context_text = "Tidak ada konteks relevan."
    else:
        context_parts = []
        for record in retrieve_data:
            # Ambil nilai field sesuai field_name
            field_value = record.get(field_name, "")
            if field_value:
                context_parts.append(field_value.strip())

        # Jika tidak ada data di field tersebut
        context_text = "\n\n".join(context_parts) if context_parts else f"Tidak ada data pada field '{field_name}'."
        print(f"Context Text for {nama_posisi}:\n{context_text}\n")

    # Buat user prompt
    user_prompt = f"""
Buatkan Job Responsibilities minimal 1 tugas/jr untuk posisi bawahan berikut:
Nama Posisi: {nama_posisi}
Band Posisi: {band_posisi}

Berikut List tugas-tugas atasan dari posisi {nama_posisi}:
{context_text}

Instruksi:
- BACA SEMUA list data atasan yang diberikan, pilih minimal 1 yang paling relevan dengan nama posisi dari tugas atasannya.
- Ubah kata kerja depan dengan kata kerja sesuai panduan kata band 4,5,6, dan Senior Officer yang disediakan dan jangan asal.
- Jangan menambah atau mengubah isi aktivitas utama selain kata kerja depannya.
- Hasil akhir berupa list Job Responsibilities sesuai jumlah yang ditentukan.
- Setiap list item dipisahkan dengan tanda strip (-).
- Output hanya list JR tanpa catatan atau penjelasan tambahan!
"""

    system_prompt = f"""
Tugasmu adalah membuat Job Responsibilities (JR).\n\nIkuti langkah berikut:\n1) Rumus JR = [Kata Kerja + Aktivitas utama dari atasan]. Gunakan kata kerja sesuai pedoman band/posisi.\n2) JR diturunkan dari JR atasan yang diberikan user. Jangan ubah atau menambah narasi aktivitas utama, hanya boleh ubah kata kerja di depan sesuai dengan panduan kata kerja band  yang sesuai dengan kaidah bahasa Indonesia.\n3) - Jumlah JR untuk tiap posisi yang diberikan minimal 1 dan boleh lebih selama masih tugas yang relevan - Pemilihan tugas harus sangat relevan dengan nama posisi/fungsi, atau memuat kata kunci spesifik dari nama posisi.\n4) Output HARUS berupa daftar Job Responsibilities spesifik sesuai band/posisi, tanpa catatan tambahan, tanpa penjelasan, tanpa disclaimer, tanpa narasi pembuka/penutup. Hanya list JR murni.\n\n Pedoman Kata Kerja Band 4,5,6, dan Senior Officer : [Memeriksa, Membandingkan, Menyebarkan, Mengumpulkan, Menginformasikan, Memberitakan, Mengadakan, Memperoleh, Mengoperasikan, Melaksanakan, Menyajikan, Memproses, Menghasilkan, Menyampaikan, Menyediakan]\n contoh Format Output yang anda bisa ikuti:\n- [Specific Responsibility 1]\n- [Specific Responsibility 2]\n- [Specific Responsibility 3]\n\nIngat: Output TIDAK BOLEH memuat catatan atau keterangan tambahan dalam situasi apapun.
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response:
        job_responsibilities = response.strip()
        job_responsibilities = (
            job_responsibilities
            .replace("- ", "• ")
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )
        return job_responsibilities
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."
