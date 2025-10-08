from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from utils import postgredb_apilogy
from typing import List
from agents.djm.band_bawah.mission_statement import ms_agent
from agents.djm.band_bawah.job_responsibilities import jr_agent
from agents.djm.band_bawah.job_performance import jp_agent
from agents.djm.band_bawah.job_authorities import ja_agent
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


# Terima LIST of DJMData
async def handle_create_djm_bawah(user_id: str, data: List[DJMData]):
    try:
        await store_multiple_djm_in_db(user_id, data)

        pool = postgredb_apilogy.pool
        async with pool.acquire() as conn:
            table_name = f"excel_djm_{user_id}"
            query = f"""
                SELECT jobid, nama_posisi, band_posisi, atasan 
                FROM "{table_name}"
                WHERE band_posisi IN ('IV', 'V', 'VI')
            """
            rows = await conn.fetch(query)

        djm_results = await get_djm_atas(user_id)

        # for row in rows:
        for row in rows:
            job_id = row["jobid"]
            nama_posisi = row["nama_posisi"]
            atasan = row["atasan"]
            band_posisi = row["band_posisi"]

            if not nama_posisi:
                mission_statement = job_responsibilities = job_performance = job_authorities = "Nama posisi kosong"
            else:
                retrieve_data = await retrieve_position_bawah(user_id, atasan)
                mission_statement = ms_agent(nama_posisi, retrieve_data)
                job_responsibilities = jr_agent(nama_posisi, band_posisi, retrieve_data)
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

async def get_djm_atas(user_id: str):
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
