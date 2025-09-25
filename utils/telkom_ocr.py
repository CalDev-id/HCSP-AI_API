import httpx
from typing import List, Dict
from utils.embedding import API_KEY

OCR_URL = "https://telkom-ai-dag.api.apilogy.id/OCR_Document_Based/0.0.5/ocr/bbox/pdf"

async def ocr_pdf_telkom(upload_file) -> List[Dict]:
    headers = {
        "Accept": "application/json",
        "x-api-key": API_KEY,
    }

    files = {
        "file": (upload_file.filename, await upload_file.read(), "application/pdf")
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OCR_URL, headers=headers, files=files)

    if response.status_code != 200:
        raise Exception(f"OCR API error {response.status_code}: {response.text}")

    result = response.json()
    pages = []
    for page_num, content in result.items():
        pages.append({
            "page": page_num,
            "content": content.get("data", "")   # langsung ambil isi teks
        })

    return pages
