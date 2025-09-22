from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
from utils import postgredb_apilogy
from typing import List
from utils.read_template import drop_excel_table

class DJMData(BaseModel):
    jobId: int
    nama_posisi: str
    mission_statement: str
    job_responsibilities: str
    job_performance: str
    job_authorities: str


# Terima LIST of DJMData
async def handle_create_djm_bawah(user_id: str, data: List[DJMData]):
    save_djm = await store_multiple_djm_in_db(user_id, data)


    # Hapus tabel excel_djm_{user_id} setelah selesai
    await drop_excel_table(user_id)
    return save_djm


async def store_multiple_djm_in_db(user_id: str, data: List[DJMData]):
    pool = postgredb_apilogy.pool
    table_name = f"djm_atas_{user_id}"

    async with pool.acquire() as conn:
        # Drop & create sekali saja
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
