import openpyxl
from io import BytesIO
from fastapi import UploadFile
from utils import postgredb_apilogy

async def extract_xlsx(file: UploadFile):
    try:
        content = await file.read()
        wb = openpyxl.load_workbook(BytesIO(content))
        sheet = wb.active
        data = [list(row) for row in sheet.iter_rows(min_row=2, values_only=True)]
        print("template file berhasil di baca")
        return data
    except Exception as e:
        raise ValueError(f"Gagal membaca XLSX: {str(e)}")


async def store_excel_in_db(user_id: str, data: list):
    pool = postgredb_apilogy.pool
    table_name = f"excel_djm_{user_id}"

    async with pool.acquire() as conn:
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        await conn.execute(f"""
            CREATE TABLE "{table_name}" (
                jobId BIGINT PRIMARY KEY,
                nama_posisi TEXT,
                band_posisi TEXT,
                atasan TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        for row in data:
            jobId, nama_posisi, band_posisi, atasan = row

            if jobId is None:
                continue

            await conn.execute(
                f"""
                INSERT INTO "{table_name}" 
                (jobId, nama_posisi, band_posisi, atasan)
                VALUES ($1, $2, $3, $4)
                """,
                int(jobId),
                nama_posisi,
                band_posisi,
                atasan
            )

    return {"status": "success", "inserted": len(data), "table": table_name}


async def drop_excel_table(user_id: str):
    pool = postgredb_apilogy.pool
    table_name = f"excel_djm_{user_id}"

    async with pool.acquire() as conn:
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    return {"status": "success", "message": f"Table {table_name} dropped"}
