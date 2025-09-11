from fastapi import UploadFile
from fastapi.responses import JSONResponse
import openpyxl
from io import BytesIO
import httpx
import logging
import traceback
from utils.utils import combine_markdown_pages, split_by_pasal

from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from fastapi.responses import JSONResponse
from Agent.DJM.mission_statement.main import ms_agent


MISTRAL_BASE_URL = "https://api.mistral.ai/v1"
logger = logging.getLogger(__name__)

# --- API Key Loader ---
def load_mistral_key():
    try:
        with open("api_mistral.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise ValueError("File api_mistral.txt tidak ditemukan")

MISTRAL_API_KEY = load_mistral_key()


# --- Setup ChromaDB (baru) ---
from chromadb import Client
from chromadb.config import Settings
from chromadb.errors import NotFoundError

client = Client(Settings(
    persist_directory="./chroma_db",
    anonymized_telemetry=False
))

collection_name = "pasal_sections"
try:
    collection = client.get_collection(name=collection_name)
except NotFoundError:
    collection = client.create_collection(name=collection_name)



# --- Load embedding model ---
embedding_model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")

def add_section_to_vector_db(section_text: str, section_id: str):
    vector = embedding_model.encode(section_text).tolist()
    collection.add(
        documents=[section_text],
        ids=[section_id],
        embeddings=[vector]
    )


# --- Ekstrak XLSX (row ke-2 ke bawah) ---
async def extract_xlsx(file: UploadFile):
    try:
        content = await file.read()
        wb = openpyxl.load_workbook(BytesIO(content))
        sheet = wb.active
        data = [list(row) for row in sheet.iter_rows(min_row=2, values_only=True)]
        print("template file berhasil di baca")
        return data
    except Exception as e:
        raise ValueError(f"Gagal membaca XLSX: {str(e)}")

# --- OCR PDF dengan Mistral ---
async def ocr_pdf(pr_file: UploadFile):
    if not pr_file.filename.lower().endswith(".pdf"):
        raise ValueError("File PDF tidak valid")

    content = await pr_file.read()
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}

    async with httpx.AsyncClient(timeout=300) as client_http:
        files = {"file": (pr_file.filename, content, "application/pdf")}
        data = {"purpose": "ocr"}
        resp = await client_http.post(f"{MISTRAL_BASE_URL}/files", headers=headers, data=data, files=files)
        if resp.status_code != 200:
            raise ValueError(f"Upload gagal: {resp.text}")
        file_id = resp.json().get("id")

        resp_url = await client_http.get(f"{MISTRAL_BASE_URL}/files/{file_id}/url", headers=headers)
        if resp_url.status_code != 200:
            raise ValueError(f"Gagal dapatkan URL: {resp_url.text}")
        signed_url = resp_url.json().get("url")

        ocr_payload = {
            "model": "mistral-ocr-latest",
            "document": {"type": "document_url", "document_url": signed_url},
            "include_image_base64": False
        }
        resp_ocr = await client_http.post(
            f"{MISTRAL_BASE_URL}/ocr",
            headers={**headers, "Content-Type": "application/json"},
            json=ocr_payload
        )
        if resp_ocr.status_code != 200:
            raise ValueError(f"OCR gagal: {resp_ocr.text}")
        print("OCR berhasil")
    return resp_ocr.json()

# --- Handler utama ---
async def handle_create_djm(pr_file: UploadFile, template_file: UploadFile):
    try:
        # 1. Ekstrak XLSX
        xlsx_data = await extract_xlsx(template_file)
        logger.info(f"XLSX berhasil dibaca: {len(xlsx_data)} rows")

        # 2. OCR PDF
        ocr_result = await ocr_pdf(pr_file)
        logger.info(f"OCR result type: {type(ocr_result)}")

        # 3. Gabungkan semua markdown halaman jadi satu teks
        combined_text = combine_markdown_pages(ocr_result)
        logger.info(f"Panjang teks gabungan OCR: {len(combined_text)} karakter")

        # 4. Pecah berdasarkan pasal + chunking
        pasal_sections = split_by_pasal(combined_text)
        logger.info(f"Jumlah pasal terpecah: {len(pasal_sections)}")

        # 5. Masukkan tiap section ke ChromaDB
        for idx, section in enumerate(pasal_sections):
            section_id = f"{pr_file.filename}_pasal_{idx}"
            add_section_to_vector_db(section.get("chunkText", ""), section_id)

        # 6. Loop setiap row di XLSX untuk panggil ms_agent
        mission_results = []
        for row in xlsx_data:
            if row and len(row) >= 2:
                job_id = row[0]
                nama_posisi = row[1]
                if not nama_posisi:
                    mission_statement = "Nama posisi kosong"
                else:
                    mission_statement = ms_agent(nama_posisi)
                mission_results.append({
                    "jobId": job_id,
                    "nama_posisi": nama_posisi,
                    "mission_statement": mission_statement
                })


        # 7. Response final hanya mission statements
        return JSONResponse(content={"results": mission_results}, status_code=200)

    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        logger.error(err_msg)
        return JSONResponse(content={"error": err_msg}, status_code=500)
