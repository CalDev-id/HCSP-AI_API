from agents.djm.band_atas.band_3.mission_statement import ms_agent
from agents.djm.band_atas.band_3.job_responsibilities import jr_agent
from agents.djm.band_atas.band_3.job_performance import jp_agent
from agents.djm.band_atas.band_3.job_authorities import ja_agent
from utils.postgredb_apilogy import (
    retrieve_position
)

async def process_band_3(conn, table_temp, rows_band_3, user_id):
    results = []
    await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS jr_kepake_{user_id} (
            id INTEGER PRIMARY KEY,
            atasan TEXT UNIQUE,
            job_responsibilities TEXT
        );
    """)
    for row in rows_band_3[:8]:
        job_id = row["jobid"]
        nama_posisi = row["nama_posisi"]
        band_posisi = row["band_posisi"]
        atasan = row["atasan"]

        if not nama_posisi:
            mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
        else:
            retrieve_data = await retrieve_position(user_id, atasan)

            jr_kepake_rows = await conn.fetch(
                f'SELECT job_responsibilities FROM jr_kepake_{user_id} WHERE atasan ILIKE $1',
                atasan
            )

            jr_kepake = [row["job_responsibilities"] for row in jr_kepake_rows] if jr_kepake_rows else None


            mission_statement = ms_agent(nama_posisi)
            job_responsibilities = jr_agent(nama_posisi, band_posisi, retrieve_data, jr_kepake)
            job_performance = jp_agent(nama_posisi, band_posisi, job_responsibilities)
            job_authorities = ja_agent(nama_posisi, band_posisi, retrieve_data, job_responsibilities, mission_statement)

            await conn.execute(f"""
                INSERT INTO jr_kepake_{user_id} (id, atasan, job_responsibilities)
                VALUES ($1, $2, $3)
                ON CONFLICT (atasan) DO UPDATE
                SET job_responsibilities = jr_kepake_{user_id}.job_responsibilities || E'\n' || EXCLUDED.job_responsibilities
            """, job_id, atasan, job_responsibilities)


        result = {
            "jobId": job_id,
            "nama_posisi": nama_posisi,
            "mission_statement": mission_statement,
            "job_responsibilities": job_responsibilities,
            "job_performance": job_performance,
            "job_authorities": job_authorities,
            "================": "================",
            "atasan": atasan,
            "retrieve_data": retrieve_data,
            "jr_kepake": jr_kepake,
        }
        
        # await conn.execute(f"""
        #     INSERT INTO "{table_temp}" 
        #     (jobId, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)
        #     VALUES ($1, $2, $3, $4, $5, $6)
        # """, job_id, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)

        results.append(result)
        
        # await conn.execute(f'DROP TABLE IF EXISTS jr_kepake_{user_id}')
    return results
