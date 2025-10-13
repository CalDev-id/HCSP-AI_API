from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from utils import postgredb_apilogy
from typing import List
from agents.djm.band_bawah.mission_statement import ms_agent
from agents.djm.band_bawah.job_responsibilities import jr_agent
from agents.djm.band_bawah.job_performance import jp_agent
from agents.djm.band_bawah.job_authorities import ja_agent
from agents.djm.band_bawah.job_responsibilities_am import jr_am_agent as jr_agent_am
from fastapi.responses import JSONResponse
from utils.postgredb_apilogy import retrieve_position_bawah
import traceback


class DJMData(BaseModel):
    jobId: int
    nama_posisi: str
    mission_statement: str
    job_responsibilities: str
    job_performance: str
    job_authorities: str


async def handle_create_djm_bawah(user_id: str, data: List[DJMData]):
    try:
        await store_multiple_djm_in_db(user_id, data)

        pool = postgredb_apilogy.pool
        async with pool.acquire() as conn:
            table_name = f"excel_djm_{user_id}"
            query = f"""
                SELECT jobid, nama_posisi, band_posisi, atasan 
                FROM "{table_name}"
                WHERE (
                    band_posisi IN ('IV', 'V', 'VI')
                    OR LOWER(nama_posisi) LIKE '%account manager%'
                )
                AND LOWER(nama_posisi) NOT LIKE '%head of telkom%'
            """

            rows = await conn.fetch(query)

        djm_results = await get_djm_verified(user_id)

        # 🔧 Buka koneksi baru untuk CREATE TABLE
        async with pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS jr_temp_{user_id} (
                    id SERIAL PRIMARY KEY,
                    nama_posisi TEXT UNIQUE,
                    atasan TEXT,
                    job_responsibilities TEXT
                );
            """)

        for row in rows:
            job_id = row["jobid"]
            nama_posisi = row["nama_posisi"]
            band_posisi = row["band_posisi"]
            atasan = row["atasan"]
            print(job_id)
            print(nama_posisi)
            print(band_posisi)
            print("------------------------------")

            if not nama_posisi:
                mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
            else:
                retrieve_data = await retrieve_position_bawah(user_id, atasan)
                mission_statement = ms_agent(nama_posisi)

                nama_posisi_normalized = "".join(nama_posisi.lower().split())
                if "accountmanager" in nama_posisi_normalized:
                    job_responsibilities = jr_agent_am(nama_posisi, retrieve_data)
                else:
                    async with pool.acquire() as conn:
                        existing_jr = await conn.fetchrow(f"""
                            SELECT job_responsibilities FROM jr_temp_{user_id}
                            WHERE nama_posisi = $1
                        """, nama_posisi)

                    if existing_jr:
                        print("sumber : database")
                        job_responsibilities = existing_jr["job_responsibilities"]
                    else:
                        async with pool.acquire() as conn:
                            related_positions = await conn.fetch(f"""
                                SELECT nama_posisi, band_posisi FROM excel_djm_{user_id}
                                WHERE atasan = $1
                                AND LOWER(nama_posisi) NOT LIKE '%head of telkom%'
                            """, atasan)

                        if related_positions:
                            combined_positions = "; ".join(
                                # [f"{p['nama_posisi']}, Band {p['band_posisi']}" for p in related_positions]
                                [f"{p['nama_posisi']}" for p in related_positions]
                            )

                            jr_results_list = jr_agent(combined_positions, retrieve_data)
                            print("sumber : llm")

                            async with pool.acquire() as conn:
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

                job_performance = jp_agent(nama_posisi, band_posisi, retrieve_data, job_responsibilities)
                job_authorities = ja_agent(nama_posisi, retrieve_data, band_posisi, job_responsibilities, mission_statement)

                djm_results.append({
                    "jobId": job_id,
                    "nama_posisi": nama_posisi,
                    "mission_statement": mission_statement,
                    "job_responsibilities": job_responsibilities,
                    "job_performance": job_performance,
                    "job_authorities": job_authorities,
                })

            table_temp = f"djm_verified_{user_id}"
            async with pool.acquire() as conn:
                await conn.execute(f"""
                    INSERT INTO "{table_temp}" 
                    (jobId, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, job_id, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)

        return JSONResponse(content={"results": djm_results}, status_code=200)
    
    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return JSONResponse(content={"error": err_msg}, status_code=500)


async def store_multiple_djm_in_db(user_id: str, data: List[DJMData]):
    pool = postgredb_apilogy.pool
    table_name = f"djm_verified_{user_id}"

    async with pool.acquire() as conn:
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        await conn.execute(f"""
            CREATE TABLE "{table_name}" (
                jobId BIGINT PRIMARY KEY,
                nama_posisi TEXT,
                mission_statement TEXT,
                job_responsibilities TEXT,
                job_performance TEXT,
                job_authorities TEXT
            )
        """)

        # Loop insert semua data
        for item in data:
            await conn.execute(
                f"""
                INSERT INTO "{table_name}" 
                (jobId, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                item.jobId,
                item.nama_posisi,
                item.mission_statement,
                item.job_responsibilities,
                item.job_performance,
                item.job_authorities
            )

    return {"status": "success", "inserted": len(data), "message": f"Data stored in {table_name}"}

async def get_djm_verified(user_id: str):
    pool = postgredb_apilogy.pool
    async with pool.acquire() as conn:
        table_name = f"djm_verified_{user_id}"
        query = f"""
            SELECT jobid, nama_posisi, mission_statement, job_responsibilities, job_performance, job_authorities
            FROM "{table_name}"
        """
        rows = await conn.fetch(query)

        results = []
        for row in rows:
            results.append({
                "jobId": row["jobid"],
                "nama_posisi": row["nama_posisi"],
                "mission_statement": row["mission_statement"],
                "job_responsibilities": row["job_responsibilities"],
                "job_performance": row["job_performance"],
                "job_authorities": row["job_authorities"],
            })
        return results