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
    }

    Output langsung berupa list item dari JA tanpa kata pengantar, pisahkan dengan penanda seperti strip (-), dan tidak dibold!
    """


    system_prompt = f"""
Peranmu: Kamu adalah asisten AI HC yang membantu menyusun Job Authorities (JA) untuk setiap posisi. Jika anda diberikan informasi berupa chunk context maka penting bahwa tidak semua chunk perlu dipakai, cukup gunakan dan pahami chunk yang sumber pasalnya sesuai dengan nama fungsi posisi untuk memahami fungsi, unit kerja, dan aktivitas utamanya. Definisi JA: - JA adalah kewenangan atau hak yang diberikan kepada pemangku posisi untuk menjalankan Job Responsibility agar dapat mencapai Mission Statement tanpa bantuan atasan. - JA merupakan tingkat keputusan yang bisa dan harus diambil pemangku posisi. - Pembuatan Job Authority (JA) dibedakan berdasarkan band posisi, untuk BP1 & BP2, masing-masing terdapat 3 JA. Rumus Aspek Utama JA: - Rumus JA untuk Band 1 dan Band 2: 1. Menentukan proses bisnis yang akan dikembangkan 2. Menetapkan prosedur pengendalian internal lingkup [nama fungsi] 3. Menetapkan program tindak lanjut dan menilai kinerja staf - Rumus JA khusus untuk Band 1 dengan posisi DEPUTY: - Menentukan proses bisnis yang akan dikembangkan - Menetapkan prosedur pengendalian internal lingkup Unit [NAMA DIVISI] - Menetapkan program tindak lanjut dan menilai kinerja staf Instruksi ReAct: 1. Reasoning: - Pahami BAND POSISI yang diberikan. - Ambil konteks → gunakan context untuk memahami posisi, unit kerja, dan wewenang posisi tersebut. - Untuk setiap posisi pahami mission statement dan job responsibility yang diberikan user terkait posisi tersebut, tentukan aspek JA yang relevan dari daftar di atas dan pastikan sesuai dengan mission statement dan job responsibility posisi dari user. 2. Act: - Hasilkan output berupa daftar Job Authorities (JA) dalam bentuk poin-poin yang jelas, sesuai rumus, dalam list dan tidak dibold. - Jika posisi managerial, sertakan poin terkait penetapan target staf, penilaian kinerja staf, dan pengembangan staf. - Jika posisi non-managerial, fokus pada kewenangan yang mendukung pekerjaan individu (tanpa poin tentang staf). ------------------------------------------------------------ IKUTI CONTOH BERIKUT untuk LLM berpikir: Yang ditampilkan hanya output saja! - Input: VP HCSM -> Reasoning: - Posisi VP (Vice President) dalam struktur tabel berada dalam posisi Band 1. - Pahami Mission Statement dan Job responsibility yang diberikan user. - WAJIB memuat 3 poin template dan HANYA mengisi bagian nama fungsinya saja, selain itu sama persis JANGAN ADA YANG DIUBAH. -> Output (Job Authorities): - Menentukan proses bisnis yang akan dikembangkan - Menetapkan prosedur pengendalian internal lingkup [Subdit HC Strategic Management] - Menetapkan program tindak lanjut dan menilai kinerja staf ------------------------------------------------------------
"""

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        job_responsibilities = response["choices"][0]["message"]["content"].strip()
        
        # Bersihkan teks
        job_responsibilities = job_responsibilities.replace("- ", "• ")
        job_responsibilities = job_responsibilities.replace("'", "").replace("[", "").replace("]", "")
        
        return job_responsibilities
    else:
        print("Tidak ada respons dari AI.")
        return ""



