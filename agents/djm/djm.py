from fastapi import UploadFile
from fastapi.responses import JSONResponse
import traceback
from utils.utils import combine_markdown_pages, split_by_pasal
from utils.chromadb import add_section_to_vector_db
from utils.mistral import extract_xlsx, ocr_pdf
from utils.chromadb import retrieve_documents
from agents.djm.mission_statement import ms_agent
from agents.djm.job_responsibilities import jr_agent
from agents.djm.job_performance import jp_agent
from agents.djm.job_authorities import ja_agent


# --- Handler utama ---
async def handle_create_djm(pr_file: UploadFile, template_file: UploadFile):
    try:
        # 1. Ekstrak XLSX
        xlsx_data = await extract_xlsx(template_file)

        # 2. OCR PDF
        ocr_result = await ocr_pdf(pr_file)

        # 3. Gabungkan semua markdown halaman jadi satu teks
        combined_text = combine_markdown_pages(ocr_result)

        # 4. Pecah berdasarkan pasal + chunking
        pasal_sections = split_by_pasal(combined_text)

        # 5. Masukkan tiap section ke ChromaDB
        for idx, section in enumerate(pasal_sections):
            section_id = f"{pr_file.filename}_pasal_{idx}"
            add_section_to_vector_db(section.get("chunkText", ""), section_id)

        # 6. Loop setiap row di XLSX untuk panggil ms_agent
        djm_results = []
        for row in xlsx_data:
            if row and len(row) >= 2:
                job_id = row[0]
                nama_posisi = row[1]
                if not nama_posisi:
                    mission_statement = "Nama posisi kosong"
                    job_responsibilities = "Nama posisi kosong"
                    job_performance = "Nama posisi kosong"
                    job_authorities = "Nama posisi kosong"
                else:
                    retrieve_data = retrieve_documents(nama_posisi)
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

        # 7. Response final
        return JSONResponse(content={"results": djm_results}, status_code=200)

    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return JSONResponse(content={"error": err_msg}, status_code=500)
