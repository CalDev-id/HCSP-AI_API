from agents.djm.band_atas.band_3.mission_statement import ms_agent
from agents.djm.band_atas.band_3.job_responsibilities import jr_agent
from agents.djm.band_atas.band_3.job_performance import jp_agent
from agents.djm.band_atas.band_3.job_authorities import ja_agent
from agents.djm.band_atas.band_3.job_responsibilities_hotda import jr_hotda_agent as jr_agent_hotda
from utils.postgredb_apilogy import (
    retrieve_position
)
import json

async def process_band_3(conn, table_temp, rows_band_3, user_id):
    results = []
    await conn.execute(f'DROP TABLE IF EXISTS jr_temp_{user_id}')
    await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS jr_temp_{user_id} (
            id SERIAL PRIMARY KEY,
            nama_posisi TEXT UNIQUE,
            atasan TEXT,
            job_responsibilities TEXT
        );
    """)
    for row in rows_band_3:
        job_id = row["jobid"]
        nama_posisi = (row["nama_posisi"] or "").strip()
        band_posisi = row["band_posisi"]
        atasan = row["atasan"]

        if not nama_posisi:
            mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
        else:
            retrieve_data = await retrieve_position(user_id, atasan)
            mission_statement = ms_agent(nama_posisi)

            nama_posisi_normalized = "".join(nama_posisi.lower().split())

            if "headoftelkom" in nama_posisi_normalized:
                job_responsibilities = jr_agent_hotda(nama_posisi, retrieve_data)
                print(nama_posisi_normalized)
            else:
                existing_jr = await conn.fetchrow(f"""
                        SELECT job_responsibilities FROM jr_temp_{user_id}
                        WHERE nama_posisi = $1
                    """, nama_posisi)
                if existing_jr:
                    print("sumber : database")
                    job_responsibilities = existing_jr["job_responsibilities"]
                else:
                    related_positions = await conn.fetch(f"""
                        SELECT nama_posisi, band_posisi 
                        FROM excel_djm_{user_id}
                        WHERE atasan = $1
                        AND LOWER(nama_posisi) NOT LIKE '%account manager%'
                    """, atasan)


                    if related_positions:
                        combined_positions = "; ".join(
                            # [f"{p['nama_posisi']}, Band {p['band_posisi']}" for p in related_positions]
                            [f"{p['nama_posisi']}" for p in related_positions]
                        )

                        jr_results_list = jr_agent(combined_positions, retrieve_data)
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

                        job_responsibilities = (
                            new_jr["job_responsibilities"]
                            if new_jr else "Job responsibilities tidak ditemukan setelah diproses."
                        )
                    else:
                        job_responsibilities = "Data posisi terkait tidak ditemukan."

                
            job_performance = jp_agent(nama_posisi, band_posisi, job_responsibilities)
            job_authorities = ja_agent(nama_posisi, band_posisi, retrieve_data, job_responsibilities, mission_statement)




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
        }
        
        await conn.execute(f"""
            INSERT INTO "{table_temp}" 
            (jobId, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, job_id, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)

        results.append(result)
        
    return results


