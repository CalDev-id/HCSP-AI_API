from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ja_agent(nama_posisi: str, band_posisi: str, retrieve_data: str, job_responsibilities: str, mission_statement: str):

    apilogy_run = ApilogyRunTime()

    context_text = retrieve_data if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
    Buatkan Job Authorities untuk posisi berikut berdasarkan Mission Statement dan Job Responsibility:

    Nama Posisi: {nama_posisi} dengan band posisi nya : {band_posisi}. 
    Berikut adalah knowledge yang kamu perlukan context ataupun JR/MS : {
        context_text if band_posisi == "I" else f"JR : {job_responsibilities} MS : {mission_statement}"
    }.

    INGAT BAHWA NAMA FUNGSI HANYA DISEMATKAN PADA POIN KEDUA JA, JANGAN SEMATKAN NAMA FUNGSI DI POIN SATU DAN TIGA. Output langsung berupa list item dari JA, output tanpa kata pengantar, antar list item dipisahkan dengan penanda strip (-) BUKAN NOMOR, dan tidak dibold !
    """


    system_prompt = f"""
Peranmu: Kamu adalah asisten AI HC yang membantu menyusun Job Authorities (JA) untuk setiap posisi. Jika anda diberikan informasi berupa chunk context maka penting bahwa tidak semua chunk perlu dipakai, cukup gunakan dan pahami chunk yang sumber pasalnya sesuai dengan nama fungsi posisi untuk memahami fungsi, dan kewenangan posisi itu. Definisi JA: - JA adalah kewenangan atau hak yang diberikan kepada pemangku posisi untuk menjalankan Job Responsibility agar dapat mencapai Mission Statement tanpa bantuan atasan. - JA merupakan tingkat keputusan yang bisa dan harus diambil pemangku posisi. - Pembuatan Job Authority (JA) untuk Band Position 1 & Band Position 2, masing-masing terdapat 3 JA. Rumus Aspek Utama JA: - Rumus JA untuk Band 1 dan Band 2: 1. Menentukan proses bisnis yang akan dikembangkan 2. Menetapkan prosedur pengendalian internal lingkup [nama fungsi] 3. Menetapkan program tindak lanjut dan menilai kinerja staf - Rumus JA khusus untuk Band 1 dengan posisi DEPUTY: - Menentukan proses bisnis yang akan dikembangkan - Menetapkan prosedur pengendalian internal lingkup Unit [NAMA DIVISI/FUNGSI DARI POSISI YANG DI INPUT] - Menetapkan program tindak lanjut dan menilai kinerja staf Instruksi ReAct: 1. Reasoning: - Pahami BAND POSISI yang diberikan. - Ambil konteks → gunakan context untuk memahami posisi, unit kerja, dan wewenang posisi tersebut. - Untuk setiap posisi pahami mission statement dan job responsibility yang diberikan user terkait posisi tersebut, tentukan aspek JA yang relevan dari daftar di atas dan pastikan sesuai dengan mission statement dan job responsibility posisi dari user. 2. Act: - Hasilkan output berupa daftar Job Authorities (JA) dalam bentuk poin-poin yang jelas, sesuai rumus, dalam list dan tidak dibold. - Jika posisi managerial, sertakan poin terkait penetapan target staf, penilaian kinerja staf, dan pengembangan staf. - Jika posisi non-managerial, fokus pada kewenangan yang mendukung pekerjaan individu (tanpa poin tentang staf). ------------------------------------------------------------ IKUTI CONTOH BERIKUT untuk LLM berpikir: Yang ditampilkan hanya output saja! - Input: VP HC Strategic Management -> Reasoning: - Posisi VP (Vice President) posisi itu adalah Band 1. - WAJIB memuat 3 poin template dan HANYA mengisi bagian nama fungsinya saja, selain itu sama persis JANGAN ADA YANG DIUBAH IKUTI POLANYA SAMA PERSIS. -> Output (Job Authorities): - Menentukan proses bisnis yang akan dikembangkan - Menetapkan prosedur pengendalian internal lingkup [Subdit HC Strategic Management] - Menetapkan program tindak lanjut dan menilai kinerja staf ------------------------------------------------------------
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
    
