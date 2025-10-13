from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def jr_am_agent(nama_posisi: str, retrieve_data: List[dict]):

    apilogy_run = ApilogyRunTime()

    if not retrieve_data:
      context_text = "Tidak ada konteks pasal relevan."
    else:
      context_parts = []
      for record in retrieve_data:
          job_responsibilities = record.get("job_responsibilities", "")
          context_parts.append(f"{job_responsibilities}\n\n")
        
      context_text = "\n\n".join(context_parts)
    print(nama_posisi)
    print("--------------------------------")
    print(context_text)

    user_prompt = f"""

Buatkan Job Responsibilities untuk posisi berikut => Nama Posisi bawahan : {nama_posisi}. dan berikut adalah list tugas atasan dari posisi tersebut yang kamu bisa tentukan tugasnya dan harus sesuai nama fungsi posisi tsb. Tidak mengambil semua tugas atasan tapi ambil hanya yang relevan dengan nama posisi bawahannya, jangan ringkas poinnya, ambil semua narasinya dan hanya ubah kata kerja nya : {context_text}. Outputnya langsung berupa list item dari JR tanpa kata pengantar, pisahkan dengan penanda seperti strip (-),tidak kapital dan tidak dibold!
    
    """


    system_prompt = f"""
Tugasmu adalah membuat Job Responsibilities (JR).\n\nIkuti langkah berikut:\n1) Rumus JR = [Kata Kerja + Aktivitas utama dari atasan]. wajib hanya mengubah kata kerja depan/awal kalimat JR posisi dengan menggunakan kata kerja sesuai pedoman band/posisi dan jangan ubah atau potong kalimat yang lainnya harus satu point penuh .\n2) JR diturunkan dari JR atasan yang diberikan user. Jangan ubah atau menambah narasi tugas atasannya, hanya boleh ubah kata kerja di depan sesuai dengan panduan kata kerja yang disediakan yang sesuai dengan kaidah bahasa Indonesia., jangan pula menambah tugas yag tidak ada sumbernya dari tugas atasannya, jangan berkhayal menambah tugas yang tidak ada dari tugas atasan ! \n3) Khusus untuk Posisi Account Manager (AM) atau Senior Account Manager (SAM) harus hanya memiliki tugas atau JR yang hanya berkaitan tugas seorang frontliner di Unit Bisnis yang memiliki fungsi langsung terkait pengelolaan Strategic Account di segmen Enterprise, segmen Business, segmen Government, segmen Wholesale & International, dan/atau segmen Consumer tertentu AM atau Account Manager juga bertugas sebagai Sales Lapangan yang bertemu langsung dengan Consumer.dan ingat tugas account manager itu sama tugasnya dengan account manager pada lainnya. senior AM = AM 1 = AM 2 \n 4)  - Pemilihan tugas atasan untuk bawahan harus sangat relevan dengan nama posisi/fungsi bawahan, atau memuat kata kunci spesifik dari nama posisi. jangan salin semua tugas atasan abaikan tugas atasan yang tidak relevan dengan nama posisi bawahan, jika anda memberikan tugas yang tidak relevan maka jawaban anda salah besar.\n 5) Output HARUS berupa daftar Job Responsibilities spesifik sesuai band/posisi, tanpa catatan tambahan, tanpa penjelasan, tanpa disclaimer, tanpa narasi pembuka/penutup. Hanya list JR murni.\n\nPedoman Kata Kerja :\n- Managerial/Manager: [Mencapai, Menilai, Menarik, Memastikan, Mengevaluasi, Mengidentifikasi, Meningkatkan, Menerapkan, Mengatasi, Memelihara, Memantau, Meninjau, Menetapkan, Menspesifikasi, Menstandarkan]\n- \n contoh Format Output untuk kamu ikuti:\n- [Specific Responsibility 1]\n- [Specific Responsibility 2]\n- [Specific Responsibility 3]\n\nIngat: Output TIDAK BOLEH memuat catatan atau keterangan tambahan dalam situasi apapun.
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response:
        job_authorities = response.strip()

        job_authorities = job_authorities.replace("- ", "• ")
        job_authorities = job_authorities.replace("'", "").replace("[", "").replace("]", "")

        return job_authorities
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."
