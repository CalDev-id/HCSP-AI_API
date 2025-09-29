import httpx
from typing import List, Dict
from utils.embedding import API_KEY
from pypdf import PdfReader, PdfWriter  # pakai pypdf, bukan PyPDF2
from io import BytesIO

OCR_URL = "https://telkom-ai-dag.api.apilogy.id/OCR_Document_Based/0.0.5/ocr/bbox/pdf"


async def call_ocr_api(pdf_bytes: bytes, filename: str) -> Dict:
    """Helper function panggil OCR API untuk 1 batch PDF"""
    headers = {
        "Accept": "application/json",
        "x-api-key": API_KEY,
    }

    files = {
        "file": (filename, pdf_bytes, "application/pdf")
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(OCR_URL, headers=headers, files=files)

    if response.status_code != 200:
        raise Exception(f"OCR API error {response.status_code}: {response.text}")

    return response.json()


async def ocr_pdf_telkom(upload_file) -> List[Dict]:
    # Baca PDF as bytes
    pdf_bytes = await upload_file.read()
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    total_pages = len(pdf_reader.pages)

    all_results = []
    batch_size = 20
    batch_num = 0

    for start in range(0, total_pages, batch_size):
        end = min(start + batch_size, total_pages)
        batch_num += 1

        # Buat PDF baru berisi subset halaman
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(pdf_reader.pages[i])  # di pypdf aman

        output_stream = BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        # Panggil OCR API untuk batch ini
        result = await call_ocr_api(output_stream.read(), f"{upload_file.filename}_part{batch_num}.pdf")

        # Simpan hasil dengan nomor halaman global
        for page_offset, (page_num, content) in enumerate(result.items(), start=1):
            all_results.append({
                "page": start + page_offset,   # hitung halaman sebenarnya
                "content": content.get("data", "")
            })

    return all_results
