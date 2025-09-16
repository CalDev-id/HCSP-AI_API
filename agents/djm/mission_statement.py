
from llm.groq_runtime import GroqRunTime
from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ms_agent(nama_posisi: str, retrieve_data: List[str]):
    groq_run = GroqRunTime()
    apilogy_run = ApilogyRunTime()
    # Ambil pasal/section relevan dari ChromaDB

    context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
    sekarang, buatkan mission statement untuk posisi berikut :

Nama Posisi : {nama_posisi}


Mission Statement hanya berupa teks narasi langsung sebutkan misinya tanpa ada kata pengantarnya, tanpa penanda seperti (-/*), dan tidak dibold !
    """

    system_prompt = f"""
Peranmu:
Kamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi.

Tugas Utama:
1. Pahami informasi mengenai posisi yang diberikan.
2. pahami antara posisi dan band nya :
- SGM (BAND 1)
- SM  (BAND 2)
- MGR (BAND 3)
- OFF 1 (BAND 4)
- OFF 2/3 (BAND 5/6)

2. Jika posisi dengan BAND (BP) I atau II:
   - Reasoning:
     - Gunakan data dari vector database untuk mencari informasi relevan mengenai posisi tersebut.
     - Dari informasi itu, jawab 3 pertanyaan:
       1. Untuk apa posisi ini ada di organisasi?
       2. Apa kontribusi posisi ini kepada organisasi?
       3. Strategi atau unit apa yang didukung oleh posisi ini?
   - Act:
     - Susun jawaban pertanyaan menjadi satu paragraf mission statement.

3. Jika posisi dengan BAND (BP) > II :
   - Reasoning:
     - Pahami posisi dan unitnya.
   - Act:
     - Buat mission statement dengan rumus:
       Mission Statement = “Melakukan pengelolaan fungsi ” + (nama fungsi) + “ untuk mendukung pencapaian performansi”

4. Output atau jawaban anda berupa teks bukan list hanya mengandung karakter berupa huruf atau nomor saja. 

------------------------------------------------------------

IKUTI Contoh BERIKUT :

Input:
VP DIGITAL BUSINESS STRATEGY & GOV (BP I)

Reasoning:
- Gunakan data dari vector database → dapatkan deskripsi lengkap tentang peran ini.
- Jawab pertanyaan (untuk apa ada, kontribusi, strategi/unit yang didukung).

Output (Mission Statement):
Bertanggung jawab atas kesiapan dan ketersediaan kebijakan (governance) bisnis digital, mekanisme, perencanaan strategi dan orkestrasi bisnis digital, platform digital (cloud PaaS/SaaS, horizontal platform dan vertical platform) Telkom Group dengan tujuan peningkatan valuasi, digital revenue, dan efisiensi biaya pengembangan (OPEX/CAPEX) yang mencakup pengembangan portofolio produk digital berbasis business plan, perencanaan roadmap bisnis & kapabilitas digital (talent, platform digital, dan infrastruktur digital) termasuk rencana build, buy, dan borrow, pengelolaan inisiatif investasi bisnis digital, perencanaan dan orkestrasi enterprise architecture untuk bisnis digital, perencanaan dan orkestrasi customer experience (CX) dan customer engagement Digitization, pelaksanaan orkestrasi bisnis digital dan platform digital Telkom Group yang meliputi orkestrasi pengembangan bisnis digital, partnership management, dan go to market, serta pengelolaan dan orkestrasi inovasi Digitalization Telkom Group.

------------------------------------------------------------

Input:
SO DIGITAL PLATFORM STRATEGY (BP 3)

Reasoning:
- Posisi BP > 2 → pakai rumus.

Output (Mission Statement):
Melakukan pengelolaan fungsi Digital Platform Strategy untuk mendukung pencapaian performansi.

Gunakan data dari vector database berikut dari dokumen pasal relevan:
{context_text}

"""

    # Generate response
    # response = groq_run.generate_response(system_prompt, user_prompt)
    # --- pakai Apilogy ---
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        mission_statement = response["choices"][0]["message"]["content"].strip()
        print(mission_statement)
        return mission_statement
    else:
        print("Tidak ada respons dari AI.")
        return ""