import openpyxl
from io import BytesIO
import httpx
from fastapi import UploadFile


MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

# --- API Key Loader ---
def load_mistral_key():
    try:
        with open("api_mistral.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise ValueError("File api_mistral.txt tidak ditemukan")

MISTRAL_API_KEY = load_mistral_key()


# --- Ekstrak XLSX ---
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
