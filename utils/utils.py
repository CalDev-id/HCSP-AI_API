# import re
# import openpyxl
# from io import BytesIO
# from fastapi import UploadFile
# from typing import List, Dict

# def clean_ocr_result(ocr_result: List[Dict]) -> str:
#     """
#     OCR cleaning sesuai n8n:
#     - Hapus '->'
#     - Hapus '>', '<'
#     - Hapus '←'
#     Gabungkan semua hasil jadi 1 string dengan spasi.
#     """
#     result = []
#     for page in ocr_result:
#         content = page.get("content", "")
#         if content:
#             cleaned = (
#                 content.replace("->", "")
#                 .replace(">", "")
#                 .replace("<", "")
#                 .replace("←", "")
#             )
#             result.append(cleaned)
#     return " ".join(result)

# def clean_pasal_title(title: str) -> str:
#     """
#     Bersihkan judul pasal sesuai n8n:
#     - Hapus isi dalam kurung ()
#     - Sisakan huruf dan spasi saja
#     - Rapikan spasi
#     - Lowercase
#     """
#     return (
#         re.sub(r"\([^)]*\)", " ", title)        # hapus isi dalam kurung
#         .replace("\n", " ")
#         .strip()
#         .lower()
#         .replace("  ", " ")
#         .encode("ascii", "ignore").decode()     # buang karakter non-ascii
#     )

# def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 250) -> List[str]:
#     """
#     Word-aware chunking sesuai n8n:
#     - Potong berdasarkan kata, bukan karakter
#     - Overlap dihitung perkiraan jumlah kata
#     """
#     words = text.split()
#     chunks = []
#     current_chunk = []
#     current_length = 0

#     for word in words:
#         word_length = len(word) + 1  # +1 untuk spasi
#         if current_length + word_length > chunk_size:
#             # Simpan chunk
#             chunks.append(" ".join(current_chunk))

#             # Ambil overlap kata
#             approx_word_per_overlap = max(1, overlap // 5)
#             overlap_words = current_chunk[-approx_word_per_overlap:]

#             # Mulai chunk baru
#             current_chunk = overlap_words + [word]
#             current_length = sum(len(w) + 1 for w in current_chunk)
#         else:
#             current_chunk.append(word)
#             current_length += word_length

#     if current_chunk:
#         chunks.append(" ".join(current_chunk))

#     return chunks

# def split_by_pasal(input_text: str) -> List[Dict]:
#     """
#     Split teks berdasarkan "Pasal X", cari judul, lalu chunk.
#     Output sesuai format n8n.
#     """
#     lower_text = input_text.lower()
#     sections = re.split(r"(?=pasal\s*\d+)", lower_text)
#     cleaned_sections = [s for s in sections if s.strip().startswith("pasal")]

#     output_items = []
#     for section_lower in cleaned_sections:
#         start_index = lower_text.index(section_lower)
#         section_original = input_text[start_index:start_index + len(section_lower)]

#         # Cari judul pasal (baris setelah "Pasal X")
#         pasal_title = "unknown pasal"
#         match_title = re.search(r"Pasal\s*\d+\s+([^\(\n]+)", section_original, re.I)
#         if match_title:
#             pasal_title = clean_pasal_title(match_title.group(1).strip())

#         # Chunking sesuai n8n
#         chunks = chunk_text(section_original.strip(), 1000, 250)
#         for chunk in chunks:
#             output_items.append({
#                 "pasalTitle": pasal_title,
#                 "chunkText": chunk
#             })

#     return output_items

# ==============================================================================
# import re
# from typing import List, Dict

# def clean_ocr_result(ocr_result: List[Dict]) -> str:
#     """
#     OCR cleaning sesuai n8n:
#     - Hapus '->'
#     - Hapus '>', '<'
#     - Hapus '←'
#     Gabungkan semua hasil jadi 1 string dengan spasi.
#     """
#     result = []
#     for page in ocr_result:
#         content = page.get("content", "")
#         if content:
#             cleaned = (
#                 content.replace("->", "")
#                        .replace(">", "")
#                        .replace("<", "")
#                        .replace("←", "")
#             )
#             result.append(cleaned)
#     return " ".join(result)


# def clean_pasal_title(title: str) -> str:
#     """
#     Bersihkan judul pasal sesuai n8n:
#     - Hanya huruf dan spasi
#     - Rapikan spasi
#     - Lowercase
#     """
#     title = re.sub(r"\([^)]*\)", " ", title)   # hapus isi dalam kurung
#     title = title.replace("\n", " ")
#     title = re.sub(r"[^a-zA-Z\s]", " ", title) # sisakan huruf & spasi
#     title = re.sub(r"\s+", " ", title)         # rapikan spasi
#     return title.strip().lower()


# def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
#     """
#     Word-aware chunking sesuai n8n:
#     - Potong berdasarkan kata
#     - Overlap dihitung perkiraan jumlah kata
#     """
#     words = re.split(r"\s+", text)  # rapikan spasi
#     chunks = []
#     current_chunk = []
#     current_length = 0

#     for word in words:
#         word_length = len(word) + 1  # +1 untuk spasi
#         if current_length + word_length > chunk_size:
#             chunks.append(" ".join(current_chunk))

#             # Ambil overlap kata (sama dengan n8n)
#             approx_word_per_overlap = overlap // 5
#             overlap_words = current_chunk[-approx_word_per_overlap:] if approx_word_per_overlap > 0 else []

#             # Mulai chunk baru
#             current_chunk = overlap_words + [word]
#             current_length = len(" ".join(current_chunk))
#         else:
#             current_chunk.append(word)
#             current_length += word_length

#     if current_chunk:
#         chunks.append(" ".join(current_chunk))

#     return chunks


# def split_by_pasal(input_text: str) -> List[Dict]:
#     """
#     Split teks berdasarkan "Pasal X", ambil judul, lalu chunk.
#     Output sesuai format n8n.
#     """
#     lower_text = input_text.lower()
#     sections = re.split(r"(?=pasal\s*\d+)", lower_text)
#     cleaned_sections = [s for s in sections if s.strip().startswith("pasal")]

#     output_items = []
#     for section_lower in cleaned_sections:
#         start_index = lower_text.index(section_lower)
#         section_original = input_text[start_index:start_index + len(section_lower)]

#         # Ambil judul pasal: hanya sampai newline atau tanda kurung
#         match_title = re.search(r"Pasal\s*\d+\s+([^\(\n]+)", section_original, re.I)
#         pasal_title = clean_pasal_title(match_title.group(1).strip()) if match_title else "unknown pasal"

#         # Chunking
#         chunks = chunk_text(section_original.strip(), chunk_size=1000, overlap=200)
#         for chunk in chunks:
#             output_items.append({
#                 "pasalTitle": pasal_title,
#                 "chunkText": f"sumber pasal : {pasal_title}. {chunk}"
#             })

#     return output_items


#baru bangettt 
#==============================================================================


import re
from typing import List, Dict

def clean_ocr_result(ocr_result: List[Dict]) -> str:

    result = []
    for page in ocr_result:
        content = page.get("content", "")
        if content:
            cleaned = (
                content.replace("->", "")
                .replace(">", "")
                .replace("<", "")
                .replace("←", "")
            )
            result.append(cleaned)
    return " ".join(result)


def clean_pasal_title(title: str) -> str:

    return (
        re.sub(r"\([^)]*\)", " ", title)           # hapus isi dalam kurung
        .replace("\n", " ")
        .strip()
        .lower()
        .replace("  ", " ")
        .encode("ascii", "ignore").decode()        # buang karakter non-ascii
        .replace("\n", " ")
    )


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 250) -> List[str]:

    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 untuk spasi
        if current_length + word_length > chunk_size:
            # Simpan chunk
            chunks.append(" ".join(current_chunk))

            # Ambil overlap kata
            approx_word_per_overlap = max(1, overlap // 5)
            overlap_words = current_chunk[-approx_word_per_overlap:]

            # Mulai chunk baru
            current_chunk = overlap_words + [word]
            current_length = sum(len(w) + 1 for w in current_chunk)
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def split_by_pasal(input_text: str) -> Dict:

    lower_text = input_text.lower()
    sections = re.split(r"(?=pasal\s*\d+)", lower_text)
    cleaned_sections = [s for s in sections if s.strip().startswith("pasal")]

    output_items = []
    for section_lower in cleaned_sections:
        start_index = lower_text.index(section_lower)
        section_original = input_text[start_index:start_index + len(section_lower)]

        # Cari judul pasal
        pasal_title = "unknown pasal"
        match_title = re.search(r"Pasal\s*\d+\s+([^\(\n]+)", section_original, re.I)
        if match_title:
            pasal_title = clean_pasal_title(match_title.group(1).strip())

        # Chunking sesuai n8n
        chunks = chunk_text(section_original.strip(), 1000, 250)
        for chunk in chunks:
            output_items.append({
                "pasalTitle": pasal_title,
                "chunkText": f"sumber pasal : {pasal_title}. {chunk}"
            })
    return output_items
