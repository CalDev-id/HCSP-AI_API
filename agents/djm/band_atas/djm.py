from fastapi import UploadFile
from fastapi.responses import JSONResponse
import traceback
# from utils.utils import clean_ocr_result, split_by_pasal
from utils.read_template import extract_xlsx, store_excel_in_db
from utils.apilogy_ocr import ocr_pdf_apilogy
from utils import postgredb_apilogy
from utils.postgredb_apilogy import (
    create_user_table, 
    add_section, 
    retrieve_documents, 
    drop_user_table,
    retrieve_position
)
from agents.djm.band_atas.mission_statement import ms_agent
from agents.djm.band_atas.job_responsibilities import jr_agent
from agents.djm.band_atas.job_performance import jp_agent
from agents.djm.band_atas.job_authorities import ja_agent

from agents.djm.band_atas.band_3.mission_statement import ms_agent as ms_agent3
from agents.djm.band_atas.band_3.job_responsibilities import jr_agent as jr_agent3
from agents.djm.band_atas.band_3.job_performance import jp_agent as jp_agent3
from agents.djm.band_atas.band_3.job_authorities import ja_agent as ja_agent3
from utils.easy_ocr import ocr_pdf_easyocr
from utils.telkom_ocr import ocr_pdf_telkom
from utils.utils import combine_extracted_text, process_pasal_sections
from llm.apilogy_runtime import ApilogyRunTime


# ============ FUNGSI UNTUK BAND 1 & 2 ============
import json

async def process_band_1_2(conn, table_temp, rows_band_1_2, user_id):
    rows_metadata = await conn.fetch(f'SELECT id, metadata FROM data_pr_{user_id}')

    metadata_dict = {}
    for r in rows_metadata:
        meta = r["metadata"]
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                meta = {}
        metadata_dict[str(r["id"])] = meta

    print(f"Metadata dict: {metadata_dict}")
    print ("----------------------------------------------------------------------")

    results = []
    for row in rows_band_1_2[:2]:
        job_id = row["jobid"]
        nama_posisi = row["nama_posisi"]
        band_posisi = row["band_posisi"]

        if not nama_posisi:
            mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
        else:
            id_data_pr = cari_posisi_sama(nama_posisi, metadata_dict)
            id_data_pr = int(id_data_pr)
            print(f"ID data_pr ditemukan: {id_data_pr} untuk posisi {nama_posisi}")
            print ("----------------------------------------------------------------------")

            if id_data_pr == "0":
                retrieve_ms = await retrieve_documents(user_id, nama_posisi)
                retrieve_jr = await retrieve_documents(user_id, f'aktivitas utama dari {nama_posisi}')
                retrieve_ja = await retrieve_documents(user_id, f'wewenang, kewenangan atau hak dari {nama_posisi}')
            else:
                retrieve = await conn.fetchrow(
                    f'SELECT id, content, metadata FROM data_pr_{user_id} WHERE id = $1',
                    id_data_pr
                )
                print (f"Row ditemukan: {retrieve} untuk posisi {nama_posisi}")
                print ("----------------------------------------------------------------------")
                if retrieve:
                    retrieve_ms = [retrieve["content"]]
                    retrieve_jr = [retrieve["content"]]
                    retrieve_ja = [retrieve["content"]]
                else:
                    retrieve_ms = retrieve_jr = retrieve_ja = []


            mission_statement = ms_agent(nama_posisi, band_posisi, retrieve_ms)
            job_responsibilities = jr_agent(nama_posisi, band_posisi, retrieve_jr)
            job_performance = jp_agent(nama_posisi, band_posisi, job_responsibilities)
            job_authorities = ja_agent(nama_posisi, band_posisi, retrieve_ja, job_responsibilities, mission_statement)

        result = {
            "jobId": job_id,
            "nama_posisi": nama_posisi,
            "mission_statement": mission_statement,
            "job_responsibilities": job_responsibilities,
            "job_performance": job_performance,
            "job_authorities": job_authorities,
        }

        await conn.execute(f"""
            INSERT INTO "{table_temp}" (jobId, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, job_id, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)

        results.append(result)

    return results


# ============ FUNGSI UNTUK BAND 3 ============
async def process_band_3(conn, table_temp, rows_band_3, user_id):
    results = []
    for row in rows_band_3[:2]:
        job_id = row["jobid"]
        nama_posisi = row["nama_posisi"]
        band_posisi = row["band_posisi"]
        atasan = row["atasan"]

        if not nama_posisi:
            mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
        else:
            retrieve_data = await retrieve_position(user_id, atasan)

            mission_statement = ms_agent3(nama_posisi, band_posisi, retrieve_data)
            job_responsibilities = jr_agent3(nama_posisi, band_posisi, retrieve_data)
            job_performance = jp_agent3(nama_posisi, band_posisi, job_responsibilities)
            job_authorities = ja_agent3(nama_posisi, band_posisi, retrieve_data, job_responsibilities, mission_statement)

        result = {
            "jobId": job_id,
            "nama_posisi": nama_posisi,
            "mission_statement": mission_statement,
            "job_responsibilities": job_responsibilities,
            "job_performance": job_performance,
            "job_authorities": job_authorities,
        }

        results.append(result)

    return results


# ============ HANDLE MAIN FUNCTION ============
async def handle_create_djm(user_id: str, pr_file: UploadFile, template_file: UploadFile):

    try:
        await create_user_table(user_id)
        ocr_result = await ocr_pdf_telkom(pr_file)
        # ocr_result = await ocr_pdf_apilogy(pr_file)

        combined_text = combine_extracted_text(ocr_result)
        pasal_sections = process_pasal_sections(combined_text)

        for section in pasal_sections:
            await add_section(
                user_id,
                section.get("chunkText", ""),
                section.get("pasalTitle", "unknown")
            )

        xlsx_data = await extract_xlsx(template_file)
        await store_excel_in_db(user_id, xlsx_data)

        pool = postgredb_apilogy.pool
        async with pool.acquire() as conn:
            table_excel = f"excel_djm_{user_id}"
            table_temp = f"djm_12_temp_{user_id}"

            await conn.execute(f'DROP TABLE IF EXISTS "{table_temp}"')
            await conn.execute(f"""
                CREATE TABLE "{table_temp}" (
                    jobId BIGINT,
                    nama_posisi TEXT,
                    mission_statement TEXT,
                    job_responsibilities TEXT,
                    job_performance TEXT,
                    job_authorities TEXT
                )
            """)

            query_band_1_2 = f"""
                SELECT jobid, nama_posisi, band_posisi, atasan 
                FROM "{table_excel}"
                WHERE band_posisi IN ('I', 'II')
            """
            rows_band_1_2 = await conn.fetch(query_band_1_2)

            query_band_3 = f"""
                SELECT jobid, nama_posisi, band_posisi, atasan 
                FROM "{table_excel}"
                WHERE band_posisi = 'III'
            """
            rows_band_3 = await conn.fetch(query_band_3)

            djm_results = []

            # proses band 1 & 2
            djm_results.extend(await process_band_1_2(conn, table_temp, rows_band_1_2, user_id))

            # proses band 3
            # djm_results.extend(await process_band_3(conn, table_temp, rows_band_3, user_id))

        return JSONResponse(content={"results": djm_results}, status_code=200)

    except Exception as e:
        # await drop_user_table(user_id)
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return JSONResponse(content={"error": err_msg}, status_code=500)


def cari_posisi_sama(nama_posisi, metadata_dict):
    apilogy_run = ApilogyRunTime()

    metadata_text = "\n".join(
        [f"Sumber ID : {mid} || Sumber pasal : {meta.get('pasalTitle','') if isinstance(meta, dict) else str(meta)}"
         for mid, meta in metadata_dict.items()]
    )

    user_prompt = f"""
Sekarang cari yang benar dan ambilah satu id chunk pasal yang memuat nama posisi 
atau paling relevan dengan posisi berikut : {nama_posisi}. 
Berikut chunk pasal yang harus anda periksa : 
{metadata_text}
    """

    system_prompt = """
Tugas Anda adalah mengambil id pasal yang memiliki sumber pasal sangat relevan atau memuat nama posisi yang diberikan. 
Pastikan nama jabatan atau nama posisi terdapat di sumber pasalnya, jika tidak ada maka cari yang paling relevan. 
Berikan hanya 1 ID sumber dari chunk yang relevan. Jangan menambahkan kalimat pengantar. 
Pahami singkatan atau akronim pada nama jabatan, misal SGM = Senior General Manager, 
MGR = Manager, HC = Human Capital, VP = Vice President, dll. 
Jika tidak ditemukan chunk yang relevan, cukup keluarkan 0.
Contoh:
INPUT : SGM HC COMMUNICATION
Data chunk : Sumber ID : 5 || Sumber pasal : Senior General Manager HC Communication.
OUTPUT : 5
    """

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        id_result = response["choices"][0]["message"]["content"].strip()
        print(f"Posisi cocok: {id_result}")
        return id_result
    else:
        print("Tidak ada respons dari AI.")
        return "0"