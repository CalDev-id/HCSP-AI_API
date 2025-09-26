from fastapi import UploadFile
from fastapi.responses import JSONResponse
import traceback
from utils.utils import clean_ocr_result, split_by_pasal
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


# ============ FUNGSI UNTUK BAND 1 & 2 ============
async def process_band_1_2(conn, table_temp, rows_band_1_2, user_id):
    results = []
    for row in rows_band_1_2[:2]:
        job_id = row["jobid"]
        nama_posisi = row["nama_posisi"]
        band_posisi = row["band_posisi"]

        if not nama_posisi:
            mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
        else:
            retrieve_ms = await retrieve_documents(user_id, nama_posisi)
            retrieve_jr = await retrieve_documents(user_id, 'aktivitas utama dari ' + nama_posisi)
            retrieve_ja = await retrieve_documents(user_id, 'wewenang, kewenangan atau hak dari ' + nama_posisi)

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
        # return JSONResponse(content={"ocr_result": ocr_result}, status_code=200)

        cleaned_text = clean_ocr_result(ocr_result)
        pasal_sections = split_by_pasal(cleaned_text)

        for idx, section in enumerate(pasal_sections):
            section_id = f"{pr_file.filename}_pasal_{idx}"
            await add_section(
                user_id,
                section.get("chunkText", ""),
                section_id,
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
            djm_results.extend(await process_band_3(conn, table_temp, rows_band_3, user_id))

        return JSONResponse(content={"results": djm_results}, status_code=200)

    except Exception as e:
        # await drop_user_table(user_id)
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return JSONResponse(content={"error": err_msg}, status_code=500)


