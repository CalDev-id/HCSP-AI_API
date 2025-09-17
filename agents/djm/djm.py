
#versi masih excel tapi work

# import uuid
# from fastapi import UploadFile
# from fastapi.responses import JSONResponse
# import traceback
# from utils.utils import combine_markdown_pages, split_by_pasal, extract_xlsx
# from utils.apilogy_ocr import ocr_pdf_apilogy
# from utils.postgredb import (
#     create_user_table, 
#     add_section, 
#     retrieve_documents, 
#     drop_user_table
# )
# from agents.djm.mission_statement import ms_agent
# from agents.djm.job_responsibilities import jr_agent
# from agents.djm.job_performance import jp_agent
# from agents.djm.job_authorities import ja_agent
# import json
# import re
# from llm.groq_runtime import GroqRunTime

# async def handle_create_djm(pr_file: UploadFile, template_file: UploadFile):
#     # Buat user_id unik untuk tabel sementara
#     user_id = str(uuid.uuid4()).replace("-", "_")

#     try:
#         # 1. Buat tabel khusus user
#         await create_user_table(user_id)

#         # 2. Ambil data dari template
#         xlsx_data = await extract_xlsx(template_file)

#         # 3. OCR file PDF
#         ocr_result = await ocr_pdf_apilogy(pr_file)

#         # 4. Gabungkan isi markdown
#         combined_text = combine_markdown_pages(ocr_result)

#         posisi_text = extract_positions_section(combined_text)

#         # 5. Split per pasal
#         pasal_sections = split_by_pasal(combined_text)

#         # 6. Masukkan tiap pasal ke tabel unik user
#         for idx, section in enumerate(pasal_sections):
#             section_id = f"{pr_file.filename}_pasal_{idx}"
#             await add_section(user_id, section.get("chunkText", ""), section_id)

#         # 7. Proses DJM
#         djm_results = []
#         for row in xlsx_data:
#             if row and len(row) >= 2:
#                 job_id = row[0]
#                 nama_posisi = row[1]
#                 if not nama_posisi:
#                     mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
#                 else:
#                     retrieve_data = await retrieve_documents(user_id, nama_posisi)
#                     mission_statement = ms_agent(nama_posisi, retrieve_data)
#                     job_responsibilities = jr_agent(nama_posisi, retrieve_data)
#                     job_performance = jp_agent(nama_posisi, retrieve_data, job_responsibilities)
#                     job_authorities = ja_agent(nama_posisi, retrieve_data, job_responsibilities, mission_statement)

#                 djm_results.append({
#                     "jobId": job_id,
#                     "nama_posisi": nama_posisi,
#                     "mission_statement": mission_statement,
#                     "job_responsibilities": job_responsibilities,
#                     "job_performance": job_performance,
#                     "job_authorities": job_authorities,
#                 })

#         # ✅ Hapus tabel user setelah selesai
#         await drop_user_table(user_id)

#         # 8. Response final
#         return JSONResponse(content={"results": djm_results}, status_code=200)

#     except Exception as e:
#         # Kalau error, tetap hapus tabel biar gak nyisa
#         await drop_user_table(user_id)
#         err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
#         return JSONResponse(content={"error": err_msg}, status_code=500)




# def extract_positions_section(text: str) -> list[dict]:
#     clean_text = re.sub(r"\s+", " ", text)

#     pattern = re.compile(
#         r"(DAFTAR\s+POSISI\s+DAN\s+FORMASI\s+ORGANISASI.*?)(?=LAMPIRAN\s+III)",
#         re.IGNORECASE
#     )
#     match = pattern.search(clean_text)

#     groq_run = GroqRunTime()
#     user_prompt = f"""
#     tolong rapihkan posisi berikut sesuai format output. rapihkan tanpa kata pengantar, langsung format json :
#     {match.group(1).strip() if match else "Teks posisi tidak ditemukan"}
#     """

#     system_prompt = """
# Anda adalah asisten Human Capital (HC).  
# Tugas Anda adalah merapihkan input user supaya menjadi format JSON dengan field:
# - "posisi"
# - "atasan"

# * PENTING ! * Catatan:
# - input user adalah daftar posisi yang sudah diurutkan per-team, dimana manager akan selalu berpasangan bersama dengan managernya, begitupun manager diatasnya pasti SM yang sesuai dengan dia, artinya urutan di input user sudah urut, tugas anda hanya merapihkan table nya supaya keliatan siapa atasannya saja, posisi jangan dihapus, diubah urutannya, atau ditambah.
# - Posisi tertinggi ditandai dengan "atasan": "-"
# - Setiap posisi lain memiliki nilai "fungsi" sesuai posisi di atasnya. "nama posisi + {nama fungsi}" contoh. SM HC +{subsidiaries and support}

# Contoh output:
# [
#   { "posisi": "SGM HCSP", "atasan": "-" },
#   { "posisi": "SM HCSP I", "atasan": "SGM HCSP" }
# ]
#     """

#     # Panggil Groq
#     response = groq_run.generate_response(system_prompt, user_prompt)

#     if response and hasattr(response.choices[0].message, "content"):
#         raw_output = response.choices[0].message.content.strip()

#         # --- Bersihkan blok markdown ---
#         cleaned = (
#             raw_output
#             .replace("```json", "")
#             .replace("```", "")
#             .strip()
#         )
#         # Buang semua sebelum tanda [ pertama
#         if "[" in cleaned:
#             cleaned = cleaned[cleaned.index("["):]

#         # --- Parse JSON ---
#         try:
#             parsed = json.loads(cleaned)
#             return parsed  # langsung list of dict
#         except Exception as e:
#             print("Gagal parse JSON:", e)
#             print("Isi yang gagal diparse:\n", cleaned)
#             return []
#     else:
#         print("Tidak ada respons dari AI.")
#         return []



# #=============================================================================================
# import uuid
# from fastapi import UploadFile
# from fastapi.responses import JSONResponse
# import traceback
# from utils.utils import combine_markdown_pages, split_by_pasal, extract_xlsx
# from utils.apilogy_ocr import ocr_pdf_apilogy
# from utils.postgredb import (
#     create_user_table, 
#     add_section, 
#     retrieve_documents, 
#     drop_user_table
# )
# from agents.djm.mission_statement import ms_agent
# from agents.djm.job_responsibilities import jr_agent
# from agents.djm.job_performance import jp_agent
# from agents.djm.job_authorities import ja_agent
# import json
# import re
# from llm.groq_runtime import GroqRunTime

# async def handle_create_djm(pr_file: UploadFile):
#     user_id = str(uuid.uuid4()).replace("-", "_")

#     try:
#         await create_user_table(user_id)

#         ocr_result = await ocr_pdf_apilogy(pr_file)

#         combined_text = combine_markdown_pages(ocr_result)

#         posisi_list = extract_positions_section(combined_text)

#         pasal_sections = split_by_pasal(combined_text)

#         for idx, section in enumerate(pasal_sections):
#             section_id = f"{pr_file.filename}_pasal_{idx}"
#             await add_section(user_id, section.get("chunkText", ""), section_id)

#         djm_results = []
#         # for idx, row in enumerate(posisi_list):
#         for idx, row in enumerate(posisi_list[:2]):
#             nama_posisi = row.get("posisi")
#             if not nama_posisi:
#                 mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
#             else:
#                 retrieve_data = await retrieve_documents(user_id, nama_posisi)
#                 mission_statement = ms_agent(nama_posisi, retrieve_data)
#                 job_responsibilities = jr_agent(nama_posisi, retrieve_data)
#                 job_performance = jp_agent(nama_posisi, retrieve_data, job_responsibilities)
#                 job_authorities = ja_agent(nama_posisi, retrieve_data, job_responsibilities, mission_statement)

#             djm_results.append({
#                 "jobId": f"posisi_{idx+1}",   # nanti ganti pliss T_T
#                 "nama_posisi": nama_posisi,
#                 "mission_statement": mission_statement,
#                 "job_responsibilities": job_responsibilities,
#                 "job_performance": job_performance,
#                 "job_authorities": job_authorities,
#             })

#         await drop_user_table(user_id)

#         return JSONResponse(content={"results": djm_results}, status_code=200)

#     except Exception as e:
#         await drop_user_table(user_id)
#         err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
#         return JSONResponse(content={"error": err_msg}, status_code=500)



# def extract_positions_section(text: str) -> list[dict]:
#     clean_text = re.sub(r"\s+", " ", text)

#     pattern = re.compile(
#         r"(DAFTAR\s+POSISI\s+DAN\s+FORMASI\s+ORGANISASI.*?)(?=LAMPIRAN\s+III)",
#         re.IGNORECASE
#     )
#     match = pattern.search(clean_text)

#     groq_run = GroqRunTime()
#     user_prompt = f"""
#     tolong rapihkan posisi berikut sesuai format output. rapihkan tanpa kata pengantar, langsung format json :
#     {match.group(1).strip() if match else "Teks posisi tidak ditemukan"}
#     """

#     system_prompt = """
# Anda adalah asisten Human Capital (HC).  
# Tugas Anda adalah merapihkan input user supaya menjadi format JSON dengan field:
# - "posisi"
# - "atasan"

# * PENTING ! * Catatan:
# - input user adalah daftar posisi yang sudah diurutkan per-team, dimana manager akan selalu berpasangan bersama dengan managernya, begitupun manager diatasnya pasti SM yang sesuai dengan dia, artinya urutan di input user sudah urut, tugas anda hanya merapihkan table nya supaya keliatan siapa atasannya saja, posisi jangan dihapus, diubah urutannya, atau ditambah.
# - Posisi tertinggi ditandai dengan "atasan": "-"
# - Setiap posisi lain memiliki nilai "fungsi" sesuai posisi di atasnya. "nama posisi + {nama fungsi}" contoh. SM HC +{subsidiaries and support}

# Contoh output:
# [
#   { "posisi": "SGM HCSP", "atasan": "-" },
#   { "posisi": "SM HCSP I", "atasan": "SGM HCSP" }
# ]
#     """

#     # Panggil Groq
#     response = groq_run.generate_response(system_prompt, user_prompt)

#     if response and hasattr(response.choices[0].message, "content"):
#         raw_output = response.choices[0].message.content.strip()

#         # --- Bersihkan blok markdown ---
#         cleaned = (
#             raw_output
#             .replace("```json", "")
#             .replace("```", "")
#             .strip()
#         )
#         # Buang semua sebelum tanda [ pertama
#         if "[" in cleaned:
#             cleaned = cleaned[cleaned.index("["):]

#         # --- Parse JSON ---
#         try:
#             parsed = json.loads(cleaned)
#             return parsed  # langsung list of dict
#         except Exception as e:
#             print("Gagal parse JSON:", e)
#             print("Isi yang gagal diparse:\n", cleaned)
#             return []
#     else:
#         print("Tidak ada respons dari AI.")
#         return []



import uuid
from fastapi import UploadFile
from fastapi.responses import JSONResponse
import traceback
from utils.utils import combine_markdown_pages, split_by_pasal, extract_xlsx
from utils.apilogy_ocr import ocr_pdf_apilogy
from utils.postgredb_apilogy import (
    create_user_table, 
    add_section, 
    retrieve_documents, 
    drop_user_table
)
from agents.djm.mission_statement import ms_agent
from agents.djm.job_responsibilities import jr_agent
from agents.djm.job_performance import jp_agent
from agents.djm.job_authorities import ja_agent
import json
import re
from llm.groq_runtime import GroqRunTime

async def handle_create_djm(pr_file: UploadFile):
    user_id = str(uuid.uuid4()).replace("-", "_")

    try:
        await create_user_table(user_id)

        ocr_result = await ocr_pdf_apilogy(pr_file)

        combined_text = combine_markdown_pages(ocr_result)

        posisi_list = extract_positions_section(combined_text)

        pasal_sections = split_by_pasal(combined_text)

        for idx, section in enumerate(pasal_sections):
            section_id = f"{pr_file.filename}_pasal_{idx}"
            await add_section(user_id, section.get("chunkText", ""), section_id)

        djm_results = []
        # for idx, row in enumerate(posisi_list):
        for idx, row in enumerate(posisi_list[:2]):
            nama_posisi = row.get("posisi")
            if not nama_posisi:
                mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
            else:
                retrieve_data = await retrieve_documents(user_id, nama_posisi)
                mission_statement = ms_agent(nama_posisi, retrieve_data)
                job_responsibilities = jr_agent(nama_posisi, retrieve_data)
                job_performance = jp_agent(nama_posisi, retrieve_data, job_responsibilities)
                job_authorities = ja_agent(nama_posisi, retrieve_data, job_responsibilities, mission_statement)

            djm_results.append({
                "jobId": f"posisi_{idx+1}",   # nanti ganti pliss T_T
                "nama_posisi": nama_posisi,
                "mission_statement": mission_statement,
                "job_responsibilities": job_responsibilities,
                "job_performance": job_performance,
                "job_authorities": job_authorities,
            })

        await drop_user_table(user_id)

        return JSONResponse(content={"results": djm_results}, status_code=200)

    except Exception as e:
        await drop_user_table(user_id)
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return JSONResponse(content={"error": err_msg}, status_code=500)



def extract_positions_section(text: str) -> list[dict]:
    clean_text = re.sub(r"\s+", " ", text)

    pattern = re.compile(
        r"(DAFTAR\s+POSISI\s+DAN\s+FORMASI\s+ORGANISASI.*?)(?=LAMPIRAN\s+III)",
        re.IGNORECASE
    )
    match = pattern.search(clean_text)

    groq_run = GroqRunTime()
    user_prompt = f"""
    tolong rapihkan posisi berikut sesuai format output. rapihkan tanpa kata pengantar, langsung format json :
    {match.group(1).strip() if match else "Teks posisi tidak ditemukan"}
    """

    system_prompt = """
Anda adalah asisten Human Capital (HC).  
Tugas Anda adalah merapihkan input user supaya menjadi format JSON dengan field:
- "posisi"
- "atasan"

* PENTING ! * Catatan:
- input user adalah daftar posisi yang sudah diurutkan per-team, dimana manager akan selalu berpasangan bersama dengan managernya, begitupun manager diatasnya pasti SM yang sesuai dengan dia, artinya urutan di input user sudah urut, tugas anda hanya merapihkan table nya supaya keliatan siapa atasannya saja, posisi jangan dihapus, diubah urutannya, atau ditambah.
- Posisi tertinggi ditandai dengan "atasan": "-"
- Setiap posisi lain memiliki nilai "fungsi" sesuai posisi di atasnya. "nama posisi + {nama fungsi}" contoh. SM HC +{subsidiaries and support}

Contoh output:
[
  { "posisi": "SGM HCSP", "atasan": "-" },
  { "posisi": "SM HCSP I", "atasan": "SGM HCSP" }
]
    """

    response = groq_run.generate_response(system_prompt, user_prompt)

    if response and hasattr(response.choices[0].message, "content"):
        raw_output = response.choices[0].message.content.strip()

        cleaned = (
            raw_output
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        if "[" in cleaned:
            cleaned = cleaned[cleaned.index("["):]

        try:
            parsed = json.loads(cleaned)
            return parsed
        except Exception as e:
            print("Gagal parse JSON:", e)
            print("Isi yang gagal diparse:\n", cleaned)
            return []
    else:
        print("Tidak ada respons dari AI.")
        return []
