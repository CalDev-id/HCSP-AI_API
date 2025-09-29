


import re
from typing import List, Dict

def combine_extracted_text(ocr_result: List[Dict]) -> str:
    """
    Sama seperti node code 1 di n8n.
    Ambil semua extracted_text (di kita = content) lalu gabungkan.
    """
    combined_text = "\n\n".join(page["content"] for page in ocr_result if "content" in page)
    return combined_text


def process_pasal_sections(combined_text: str) -> List[Dict]:
    """
    Sama seperti node code 2 di n8n.
    Bersihkan text, cari pasal, lalu return list hasil.
    """
    # Bersihkan karakter *, #, '
    input_text = re.sub(r"[*#']", "", combined_text)

    # Lowercase hanya untuk cari kata 'pasal'
    lower_text = input_text.lower()

    # Cari posisi 'pasal' + angka
    pasal_positions = []
    search_pos = 0
    while True:
        match = lower_text.find("pasal", search_pos)
        if match == -1:
            break
        after_pasal = lower_text[match + 5:]
        if re.match(r"^\s*\d+", after_pasal):
            pasal_positions.append(match)
        search_pos = match + 1

    def clean_pasal_title(title: str) -> str:
        return (
            re.sub(r"\([^)]*\)", " ", title)   # hapus isi dalam kurung
            .replace("(", " ")
            .replace(")", " ")
            .encode("ascii", "ignore").decode()  # optional: buang karakter aneh
        ).strip()

    output_items = []

    for i, start_pos in enumerate(pasal_positions):
        end_pos = pasal_positions[i + 1] if i < len(pasal_positions) - 1 else len(input_text)
        section_original = input_text[start_pos:end_pos].strip()
        if not section_original:
            continue

        pasal_title = None

        # Pola 1: judul di baris setelah "Pasal xx" sebelum (1)
        match_title = re.search(r"Pasal\s*\d+\s*\n+([^\n\(]+)", section_original, re.IGNORECASE)
        if match_title:
            pasal_title = clean_pasal_title(match_title.group(1).strip())
        else:
            # Pola 2: judul inline setelah (1) sebelum 'bertanggung jawab'
            match_inline = re.search(r"\(1\)\s*(.*?)\s+bertanggung\s+jawab", section_original, re.IGNORECASE)
            if match_inline:
                pasal_title = clean_pasal_title(match_inline.group(1).strip())
            else:
                # Fallback: ambil 5 kata pertama setelah "Pasal xx"
                fallback = (
                    re.sub(r"Pasal\s*\d+", "", section_original, flags=re.IGNORECASE)
                    .strip()
                    .split()
                )
                pasal_title = clean_pasal_title(" ".join(fallback[:5]))

        output_items.append({
            "pasalTitle": pasal_title,
            "chunkText": f"sumber pasal : {pasal_title}. {section_original}"
        })

    return output_items
