


import re
from typing import List, Dict
import json
from llm.apilogy_runtime import ApilogyRunTime

def combine_extracted_text(ocr_result: List[Dict]) -> str:

    combined_text = "\n\n".join(page["content"] for page in ocr_result if "content" in page)
    return combined_text


def process_pasal_sections(combined_text: str) -> List[Dict]:

    input_text = re.sub(r"[*#']", "", combined_text)

    lower_text = input_text.lower()

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
            re.sub(r"\([^)]*\)", " ", title)
            .replace("(", " ")
            .replace(")", " ")
            .encode("ascii", "ignore").decode()
        ).strip()

    output_items = []

    for i, start_pos in enumerate(pasal_positions):
        end_pos = pasal_positions[i + 1] if i < len(pasal_positions) - 1 else len(input_text)
        section_original = input_text[start_pos:end_pos].strip()
        if not section_original:
            continue

        pasal_title = None

        match_title = re.search(r"Pasal\s*\d+\s*\n+([^\n\(]+)", section_original, re.IGNORECASE)
        if match_title:
            pasal_title = clean_pasal_title(match_title.group(1).strip())
        else:
            match_inline = re.search(r"\(1\)\s*(.*?)\s+bertanggung\s+jawab", section_original, re.IGNORECASE)
            if match_inline:
                pasal_title = clean_pasal_title(match_inline.group(1).strip())
            else:
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


async def pasal_corrector(conn, user_id: str):
    rows_metadata = await conn.fetch(f'SELECT id, metadata FROM data_pr_{user_id}')

    metadata_dict: Dict[int, dict] = {}
    for r in rows_metadata:
        meta = r["metadata"]
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                meta = {}
        metadata_dict[r["id"]] = meta 

    metadata_text = "\n".join(
        [f"ID:{mid} || {meta.get('pasalTitle','')}" for mid, meta in metadata_dict.items()]
    )

    user_prompt = f"""
Berikut daftar nama pasal, rapihkan sesuai instruksi:

{metadata_text}

Output harus dalam format JSON seperti ini:
("1": "pasalTitle_baru", "2": "pasalTitle_baru", ...)
    """

    system_prompt = """
Tugas anda adalah memperbaiki nama pasal. 
- Jika nama pasal kelebihan kata, terlalu panjang, atau berulang maka rapihkan. 
- Jika nama posisi sudah benar, biarkan saja. 
- Hasilkan output hanya dalam JSON mapping id ke pasalTitle baru, tanpa tambahan teks lain.
- Output HARUS berupa JSON object saja.
- Jangan menambahkan teks lain, penjelasan, catatan, atau format selain JSON.
Contoh:
INPUT => ID:1 || Pengertian Dalam Peraturan ini yang
OUTPUT => {"1": "Pengertian", "2": "Daftar Posisi"}

    """

    apilogy_run = ApilogyRunTime()
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if not response or "choices" not in response:
        print("Tidak ada respons dari AI.")
        return

    try:
        corrected_json = json.loads(response["choices"][0]["message"]["content"].strip())
    except json.JSONDecodeError:
        print("Gagal parsing JSON dari respons AI")
        return
    for row_id_str, new_title in corrected_json.items():
        try:
            row_id = int(row_id_str)
        except ValueError:
            continue

        if row_id in metadata_dict:
            meta = metadata_dict[row_id]
            meta["pasalTitle"] = new_title
            await conn.execute(
                f"UPDATE data_pr_{user_id} SET metadata = $1 WHERE id = $2",
                json.dumps(meta),
                row_id,
            )

    print("Update selesai.")
