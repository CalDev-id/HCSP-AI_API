
import uuid
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
    drop_user_table
)
from agents.djm.mission_statement import ms_agent
from agents.djm.job_responsibilities import jr_agent
from agents.djm.job_performance import jp_agent
from agents.djm.job_authorities import ja_agent

async def handle_create_djm(user_id: str, pr_file: UploadFile, template_file: UploadFile):
    # user_id = str(uuid.uuid4()).replace("-", "_")

    try:
        await create_user_table(user_id)

        xlsx_data = await extract_xlsx(template_file)
        await store_excel_in_db(user_id, xlsx_data)

        ocr_result = await ocr_pdf_apilogy(pr_file)
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

        pool = postgredb_apilogy.pool
        async with pool.acquire() as conn:
            table_name = f"excel_djm_{user_id}"
            query = f"""
                SELECT jobid, nama_posisi, band_posisi, atasan 
                FROM "{table_name}"
                WHERE band_posisi IN ('I', 'II')
            """
            rows = await conn.fetch(query)


        djm_results = []
        # for row in rows:
        for row in rows[:2]:
            job_id = row["jobid"]
            nama_posisi = row["nama_posisi"]

            if not nama_posisi:
                mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
            else:
                retrieve_data = await retrieve_documents(user_id, nama_posisi)
                mission_statement = ms_agent(nama_posisi, retrieve_data)
                job_responsibilities = jr_agent(nama_posisi, retrieve_data)
                job_performance = jp_agent(nama_posisi, retrieve_data, job_responsibilities)
                job_authorities = ja_agent(nama_posisi, retrieve_data, job_responsibilities, mission_statement)

                djm_results.append({
                    "jobId": job_id,
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

