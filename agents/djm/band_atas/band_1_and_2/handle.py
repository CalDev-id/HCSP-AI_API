import json
from typing import Optional, List
from utils.postgredb_apilogy import (
    retrieve_documents,
    cari_database
)
from agents.djm.band_atas.band_1_and_2.mission_statement import ms_agent
from agents.djm.band_atas.band_1_and_2.job_responsibilities import jr_agent
from agents.djm.band_atas.band_1_and_2.job_performance import jp_agent
from agents.djm.band_atas.band_1_and_2.job_authorities import ja_agent


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
    for row in rows_band_1_2[:4]:
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