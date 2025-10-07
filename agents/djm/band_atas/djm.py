from fastapi import UploadFile
from fastapi.responses import JSONResponse
import traceback
# from utils.utils import clean_ocr_result, split_by_pasal
from utils.read_template import extract_xlsx, store_excel_in_db
from utils.apilogy_ocr import ocr_pdf_apilogy
from utils import postgredb_apilogy
from utils.postgredb_apilogy import (
    create_user_table, 
    add_section, 
    retrieve_documents, 
    drop_user_table,
    retrieve_position
)
from agents.djm.band_atas.mission_statement import ms_agent
from agents.djm.band_atas.job_responsibilities import jr_agent
from agents.djm.band_atas.job_performance import jp_agent
from agents.djm.band_atas.job_authorities import ja_agent

from agents.djm.band_atas.band_3.mission_statement import ms_agent as ms_agent3
from agents.djm.band_atas.band_3.job_responsibilities import jr_agent as jr_agent3
from agents.djm.band_atas.band_3.job_performance import jp_agent as jp_agent3
from agents.djm.band_atas.band_3.job_authorities import ja_agent as ja_agent3
from utils.telkom_ocr import ocr_pdf_telkom
from utils.utils import combine_extracted_text, process_pasal_sections
from llm.apilogy_runtime import ApilogyRunTime
from typing import Dict 
import json

# ============ HANDLE MAIN FUNCTION ============
async def handle_create_djm(user_id: str, pr_file: UploadFile, template_file: UploadFile):

    try:
        await create_user_table(user_id)
        ocr_result = await ocr_pdf_telkom(pr_file)
        # ocr_result = await ocr_pdf_apilogy(pr_file)

        combined_text = combine_extracted_text(ocr_result)
        pasal_sections = process_pasal_sections(combined_text)

        for section in pasal_sections:
            await add_section(
                user_id,
                section.get("chunkText", ""),
                section.get("pasalTitle", "unknown")
            )
        # await pasal_corrector(conn=postgredb_apilogy.pool, user_id=user_id)
        xlsx_data = await extract_xlsx(template_file)
        await store_excel_in_db(user_id, xlsx_data)

        pool = postgredb_apilogy.pool
        async with pool.acquire() as conn:
            table_excel = f"excel_djm_{user_id}"
            table_temp = f"djm_12_temp_{user_id}"

            await conn.execute(f'DROP TABLE IF EXISTS "{table_temp}"')
            await conn.execute(f"""
                CREATE TABLE "{table_temp}" (
                    jobId BIGINT,
                    nama_posisi TEXT,
                    mission_statement TEXT,
                    job_responsibilities TEXT,
                    job_performance TEXT,
                    job_authorities TEXT
                )
            """)

            query_band_1_2 = f"""
                SELECT jobid, nama_posisi, band_posisi, atasan 
                FROM "{table_excel}"
                WHERE band_posisi IN ('I', 'II')
            """
            rows_band_1_2 = await conn.fetch(query_band_1_2)

            query_band_3 = f"""
                SELECT jobid, nama_posisi, band_posisi, atasan 
                FROM "{table_excel}"
                WHERE band_posisi = 'III'
            """
            rows_band_3 = await conn.fetch(query_band_3)

            djm_results = []

            # proses band 1 & 2
            djm_results.extend(await process_band_1_2(conn, table_temp, rows_band_1_2, user_id))

            # proses band 3
            djm_results.extend(await process_band_3(conn, table_temp, rows_band_3, user_id))

        return JSONResponse(content={"results": djm_results}, status_code=200)

    except Exception as e:
        # await drop_user_table(user_id)
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return JSONResponse(content={"error": err_msg}, status_code=500)

# ============ FUNGSI UNTUK BAND 1 & 2 ============

async def process_band_1_2(conn, table_temp, rows_band_1_2, user_id):
    rows_metadata = await conn.fetch(f'SELECT id, metadata FROM data_pr_{user_id}')

    metadata_dict = {}
    for r in rows_metadata:
        meta = r["metadata"]
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                meta = {}
        metadata_dict[str(r["id"])] = meta

    # print(f"Metadata dict: {metadata_dict}")
    # print ("----------------------------------------------------------------------")

    results = []
    for row in rows_band_1_2[:2]:
        job_id = row["jobid"]
        nama_posisi = row["nama_posisi"]
        band_posisi = row["band_posisi"]

        if not nama_posisi:
            mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
        else:
            id_data_pr = cari_database(nama_posisi, metadata_dict)
            id_data_pr = int(id_data_pr)
            # print(f"ID data_pr ditemukan: {id_data_pr} untuk posisi {nama_posisi}")
            # print("----------------------------------------------------------------------")

            if id_data_pr == 0:
                retrieve = await retrieve_documents(user_id, nama_posisi)
            else:
                retrieve_row = await conn.fetchrow(
                    f'SELECT id, content, metadata FROM data_pr_{user_id} WHERE id = $1',
                    id_data_pr
                )
                # print(f"Row ditemukan: {retrieve_row} untuk posisi {nama_posisi}")
                # print("----------------------------------------------------------------------")
                if retrieve_row:
                    retrieve = retrieve_row["content"]
                else:
                    retrieve = ""

            mission_statement = ms_agent(nama_posisi, band_posisi, retrieve)
            job_responsibilities = jr_agent(nama_posisi, band_posisi, retrieve)
            job_performance = jp_agent(nama_posisi, job_responsibilities)
            job_authorities = ja_agent(nama_posisi, band_posisi, retrieve, job_responsibilities, mission_statement)

            result = {
                "jobId": job_id,
                "nama_posisi": nama_posisi,
                "mission_statement": mission_statement,
                "job_responsibilities": job_responsibilities,
                "job_performance": job_performance,
                "job_authorities": job_authorities,
                "id_data_pr": id_data_pr,
                "retrieve": retrieve
            }

            await conn.execute(f"""
                INSERT INTO "{table_temp}" (jobId, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, job_id, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)

            results.append(result)

    return results


# ============ FUNGSI UNTUK BAND 3 ============
async def process_band_3(conn, table_temp, rows_band_3, user_id):
    results = []
    await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS jr_temp_{user_id} (
            id SERIAL PRIMARY KEY,
            nama_posisi TEXT UNIQUE,
            atasan TEXT,
            job_responsibilities TEXT
        );
    """)

    for row in rows_band_3[:3]:
        job_id = row["jobid"]
        nama_posisi = row["nama_posisi"]
        band_posisi = row["band_posisi"]
        atasan = row["atasan"]

        if not nama_posisi:
            mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
            retrieve_data = None
        else:
            retrieve_data = await retrieve_position(user_id, atasan)
            mission_statement = ms_agent3(nama_posisi)

            existing_jr = await conn.fetchrow(f"""
                SELECT job_responsibilities FROM jr_temp_{user_id}
                WHERE nama_posisi = $1
            """, nama_posisi)

            if existing_jr:
                print("sumber : database")
                job_responsibilities = existing_jr["job_responsibilities"]
            else:
                related_positions = await conn.fetch(f"""
                    SELECT nama_posisi, band_posisi FROM excel_djm_{user_id}
                    WHERE atasan = $1
                """, atasan)

                if related_positions:
                    combined_positions = "; ".join(
                        [f"{p['nama_posisi']}, Band {p['band_posisi']}" for p in related_positions]
                    )

                    jr_results_list = jr_agent3(combined_positions, retrieve_data)
                    print("sumber : llm")

                    for jr_data in jr_results_list:
                        nama_posisi_dari_agent = jr_data.get("posisi")
                        jr_text = jr_data.get("jr")

                        if nama_posisi_dari_agent and jr_text:
                            await conn.execute(f"""
                                INSERT INTO jr_temp_{user_id} (nama_posisi, atasan, job_responsibilities)
                                VALUES ($1, $2, $3)
                                ON CONFLICT (nama_posisi) DO UPDATE SET job_responsibilities = $3
                            """, nama_posisi_dari_agent, atasan, jr_text)

                    new_jr = await conn.fetchrow(f"""
                        SELECT job_responsibilities FROM jr_temp_{user_id}
                        WHERE nama_posisi = $1
                    """, nama_posisi)

                    job_responsibilities = new_jr["job_responsibilities"] if new_jr else "Job responsibilities tidak ditemukan setelah diproses."
                else:
                    job_responsibilities = "Data posisi terkait tidak ditemukan."

            job_performance = jp_agent3(nama_posisi, band_posisi, job_responsibilities)
            job_authorities = ja_agent3(nama_posisi, band_posisi, retrieve_data, job_responsibilities, mission_statement)

        result = {
            "jobId": job_id,
            "nama_posisi": nama_posisi,
            "mission_statement": mission_statement,
            "job_responsibilities": job_responsibilities,
            "job_performance": job_performance,
            "job_authorities": job_authorities,
        }

        await conn.execute(f"""
            INSERT INTO "{table_temp}" 
            (jobId, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, job_id, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)

        results.append(result)

    # await conn.execute(f'DROP TABLE IF EXISTS jr_kepake_{user_id}')
    return results




def cari_database(nama_posisi, metadata_dict):
    apilogy_run = ApilogyRunTime()

    metadata_text = "\n".join(
        [f"Sumber ID : {mid} || Sumber pasal : {meta.get('pasalTitle','') if isinstance(meta, dict) else str(meta)}"
         for mid, meta in metadata_dict.items()]
    )

    user_prompt = f"""
Sekarang cari yang benar dan ambilah satu id chunk pasal yang memuat nama posisi 
atau paling relevan dengan posisi berikut : {nama_posisi}. 
Berikut chunk pasal yang harus anda periksa : 
{metadata_text}
    """

    system_prompt = """
Tugas Anda adalah mengambil id pasal yang memiliki sumber pasal sangat relevan atau memuat nama posisi yang diberikan. 
Pastikan nama jabatan atau nama posisi terdapat di sumber pasalnya, jika tidak ada maka cari yang paling relevan. 
Berikan hanya 1 ID sumber dari chunk yang relevan. Jangan menambahkan kalimat pengantar. 
Pahami singkatan atau akronim pada nama jabatan, misal SGM = Senior General Manager, 
MGR = Manager, HC = Human Capital, VP = Vice President, dll. 
Jika tidak ditemukan chunk yang relevan, cukup keluarkan 0.
Contoh:
INPUT : SGM HC COMMUNICATION
Data chunk : Sumber ID : 5 || Sumber pasal : Senior General Manager HC Communication.
OUTPUT : 5
    """

    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response:
        response = response.strip()
        return response
    else:
        print("Tidak ada respons dari AI.")
        return "Tidak ada respons dari AI."


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
