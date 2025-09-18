
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
from llm.apilogy_runtime import ApilogyRunTime

async def handle_create_djm(pr_file: UploadFile, template_file: UploadFile):
    user_id = str(uuid.uuid4()).replace("-", "_")

    try:
        await create_user_table(user_id)

        xlsx_data = await extract_xlsx(template_file)

        ocr_result = await ocr_pdf_apilogy(pr_file)

        combined_text = combine_markdown_pages(ocr_result)

        pasal_sections = split_by_pasal(combined_text)

        for idx, section in enumerate(pasal_sections):
            section_id = f"{pr_file.filename}_pasal_{idx}"
            await add_section(user_id, section.get("chunkText", ""), section_id)

        djm_results = []
        for row in xlsx_data:
            if row and len(row) >= 2:
                job_id = row[0]
                nama_posisi = row[1]
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

