import re
import openpyxl
from io import BytesIO
from fastapi import UploadFile

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

def combine_markdown_pages(ocr_result):
    """
    Gabungkan semua halaman OCR (list of dict) jadi satu string.
    ocr_result: list[{"page": int, "content": str}]
    """
    if not isinstance(ocr_result, list):
        raise ValueError("ocr_result harus list of dict, bukan dict")

    return "\n\n".join(p.get("content", "") for p in ocr_result if p.get("content"))

def clean_pasal_title(title: str) -> str:
    return (
        re.sub(r"\([^)]*\)", " ", title)
        .replace("\n", " ")
        .encode("ascii", "ignore").decode()
        .strip()
        .lower()
    )

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 250):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def split_by_pasal(input_text: str):
    lower_text = input_text.lower()
    sections = re.split(r"(?=pasal\s*\d+)", lower_text)
    cleaned_sections = [s for s in sections if s.strip().startswith("pasal")]

    output_items = []
    for section_lower in cleaned_sections:
        start_index = lower_text.index(section_lower)
        section_original = input_text[start_index:start_index + len(section_lower)]

        # Cari judul pasal
        pasal_title = "unknown pasal"
        match_with_br = re.search(r"Pasal\s*\d+\s*(?:<br>|\\n)\s*([^\n]+)", section_original, re.I)

        if match_with_br:
            pasal_title = clean_pasal_title(match_with_br.group(1).strip())
        else:
            match_next_line = re.search(r"Pasal\s*\d+\s*\n+([^\n]+)", section_original, re.I)
            if match_next_line:
                pasal_title = clean_pasal_title(match_next_line.group(1).strip())

        # Buat chunk
        chunks = chunk_text(section_original.strip(), 1000, 250)
        for idx, chunk in enumerate(chunks, start=1):
            output_items.append({
                "pasalTitle": pasal_title,
                "chunkIndex": idx,
                "chunkText": f" =====\n        sumber pasal : {pasal_title}.\n\n{chunk}"
            })

    return output_items
