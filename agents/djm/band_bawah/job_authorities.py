from typing import List
from llm.apilogy_runtime import ApilogyRunTime

# def ja_agent(nama_posisi: str, retrieve_data: List[dict], band_posisi: str, job_responsibilities: str, mission_statement: str):

#     apilogy_run = ApilogyRunTime()

#     if not retrieve_data:
#       context_text = "Tidak ada konteks pasal relevan."
#     else:
#       context_parts = []
#       for record in retrieve_data:
#           jobId = record.get("jobId", "")
#           nama_posisi = record.get("nama_posisi", "")
#           mission_statement = record.get("mission_statement", "")
#           job_responsibilities = record.get("job_responsibilities", "")
#           job_performance = record.get("job_performance", "")
#           job_authorities = record.get("job_authorities", "")
#           context_parts.append(f"Job ID: {jobId}\nNama Posisi: {nama_posisi}\nMission Statement: {mission_statement}\nJob Responsibilities: {job_responsibilities}\nJob Performance: {job_performance}\nJob Authorities: {job_authorities}\n")
        
#       context_text = "\n\n".join(context_parts)
#     user_prompt = f"""
# Buatkan Job Authorization untuk posisi berikut berdasarkan MS dan JR nya: Nama Posisi : {nama_posisi}. Band Posisi :  {band_posisi}, Job Responsibility Posisi tersebut : {job_responsibilities}. Mission Statement Posisi tersebut : {mission_statement}. Outputnya langsung berupa list item dari JA dan tanpa kata pengantar, pisahkan dengan penanda seperti strip (-),tidak kapital dan tidak dibold!
#     """

#     system_prompt = f"""
# Peranmu: Kamu adalah asisten AI HC yang membantu menyusun Job Authorities (JA) untuk setiap posisi. Definisi JA: - JA adalah kewenangan yang diberikan kepada pemangku posisi untuk menjalankan Job Responsibility agar dapat mencapai Mission Statement tanpa bantuan atasan. - JA merupakan tingkat keputusan yang bisa dan harus diambil pemangku posisi. - Pembuatan Job Authority (JA) dibedakan berdasarkan band posisi, Rumus JA untuk Band posisi 4 sampai 6 harus memuat aspek berikut: 1. Penentuan prioritas pekerjaan/pembiayaan. 2. Akses aplikasi. 3. Sumber data yang digunakan. 4. Metodologi kerja. 5. Penentuan target kerja unit dan staf (untuk posisi managerial). 6. Penilaian performansi/kompetensi staf (untuk posisi managerial). 7. Pengembangan kompetensi diri dan/atau staf. Instruksi ReAct: 1. Reasoning: - Pahami BAND POSISI yang diberikan. - Untuk setiap posisi pahami mission statement dan job responsibility yang diberikan user terkait posisi tersebut, tentukan aspek JA yang relevan sesuai aturan RUMUS JA dan pastikan sesuai dengan mission statement dan job responsibility posisi dari user. 2. Act: - Hasilkan output berupa daftar Job Authorities (JA) dalam bentuk poin-poin yang jelas, sesuai rumus, dalam list ( dengan - ) dan tidak dibold.
# """
#     response = apilogy_run.generate_response(system_prompt, user_prompt)

#     if response:
#         job_authorities = response.strip()

#         job_authorities = job_authorities.replace("- ", "• ")
#         job_authorities = job_authorities.replace("'", "").replace("[", "").replace("]", "")

#         return job_authorities
#     else:
#         print("Tidak ada respons dari AI.")
#         return "Tidak ada respons dari AI."
    
def ja_agent(nama_posisi: str, retrieve_data: List[dict], band_posisi: str, job_responsibilities: str, mission_statement: str):
    ja = [
        "Menentukan prioritas pembiayaan / pekerjaan",
        "Memiliki hak akses atas aplikasi ESS / enterprise support system",
        "Menentukan sumber data",
        "Menentukan metodologi kerja",
        "Membuat sasaran kinerja individu"
    ]


    return "\n".join([f"• {item}" for item in ja])
