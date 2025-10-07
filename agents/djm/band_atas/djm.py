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
)
from agents.djm.band_atas.band_1_and_2.handle import process_band_1_2
from agents.djm.band_atas.band_3.handle import process_band_3
from utils.telkom_ocr import ocr_pdf_telkom
from utils.utils import combine_extracted_text, process_pasal_sections
from llm.apilogy_runtime import ApilogyRunTime
from typing import Dict 
import json

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
        # await pasal_corrector(conn=postgredb_apilogy.pool, user_id=user_id)
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

