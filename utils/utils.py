# utils.py

import re

def combine_markdown_pages(ocr_result):
    """
    Gabungkan semua markdown dari tiap halaman OCR.
    Mirip node n8n 'gabung semua text di ocr'
    """
    if not isinstance(ocr_result, dict):
        raise ValueError("ocr_result harus dict")
    pages = ocr_result.get("pages", [])
    return "\n\n".join(p.get("markdown", "") for p in pages)


def clean_pasal_title(title: str) -> str:
    """Bersihkan judul pasal supaya rapi, mirip n8n"""
    return (
        re.sub(r"\([^)]*\)", " ", title)             # hapus isi dalam kurung
        .replace("\n", " ")
        .encode("ascii", "ignore").decode()          # buang karakter aneh
        .strip()
        .lower()
    )


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 250):
    """Bagi teks jadi beberapa chunk dengan overlap"""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def split_by_pasal(input_text: str):
    """Split teks berdasarkan 'Pasal' dan buat chunk, mirip node n8n"""
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
