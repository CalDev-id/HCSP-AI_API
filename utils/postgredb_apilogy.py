import asyncpg
from typing import Optional
from utils.embedding import get_embedding
import json

DB_URL = "postgresql://cal:pass@localhost:5432/cal"
pool: Optional[asyncpg.pool.Pool] = None

async def init_db_pool():
    global pool
    pool = await asyncpg.create_pool(DB_URL)
    print("✅ Database pool initialized")

async def create_user_table(user_id: str):
    global pool
    async with pool.acquire() as conn:
        table_name = f'data_pr_{user_id}'
        await conn.execute(f'''
            DROP TABLE IF EXISTS "{table_name}";
            CREATE TABLE "{table_name}" (
                id TEXT PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding vector(768)
            );
        ''')
    return table_name

async def add_section(user_id: str, section_text: str, section_id: str, metadata):
    global pool
    table_name = f"data_pr_{user_id}"
    vector = get_embedding(section_text)
    vector_str = "[" + ",".join(str(x) for x in vector) + "]"

    # Kalau metadata masih string → bungkus jadi dict
    if isinstance(metadata, str):
        metadata = {"pasalTitle": metadata}

    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO "{table_name}" (id, content, metadata, embedding)
            VALUES ($1, $2, $3::jsonb, $4::vector)
            ON CONFLICT (id) DO UPDATE
            SET content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding;
            """,
            section_id, section_text, json.dumps(metadata), vector_str
        )


async def retrieve_documents(user_id: str, query_text: str, top_k: int = 10, filter_metadata: Optional[dict] = None):
    global pool
    table_name = f"data_pr_{user_id}"
    query_vector = get_embedding(query_text)
    query_vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

    filter_condition = ""
    params = [query_vector_str, top_k]

    if filter_metadata:
        filter_condition = "AND metadata @> $3"
        params.append(json.dumps(filter_metadata))

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT 
                content
            FROM "{table_name}"
            WHERE true {filter_condition}
            ORDER BY embedding <-> $1::vector
            LIMIT $2;
            """,
            *params
        )

    # Ambil semua content
    contents = [row["content"] for row in rows if row["content"]]

    # Gabungkan jadi satu string compact (pakai label Chunk)
    combined_text = " ".join(
        [f"Chunk {i+1}: {c}" for i, c in enumerate(contents)]
    )

    return combined_text

# async def retrieve_documents(user_id: str, query_text: str, top_k: int = 10):
#     global pool
#     table_name = f"data_pr_{user_id}" 
#     query_vector = get_embedding(query_text)
#     query_vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

#     async with pool.acquire() as conn:
#         rows = await conn.fetch(
#             f"""
#             SELECT 
#                 content
#             FROM "{table_name}"
#             ORDER BY (1 - (embedding <=> $1::vector)) DESC
#             LIMIT $2;
#             """,
#             query_vector_str,
#             top_k
#         )

#     # Ambil semua content
#     contents = [row["content"] for row in rows if row["content"]]

#     # Gabungkan jadi satu string compact (pakai label Chunk)
#     combined_text = " ".join(
#         [f"Chunk {i+1}: {c}" for i, c in enumerate(contents)]
#     )

#     # Sama persis dengan return n8n
#     return {
#         "combined_content": combined_text
#     }

async def drop_user_table(user_id: str):
    global pool
    table_name = f"data_pr_{user_id}"
    async with pool.acquire() as conn:
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')

async def retrieve_position_bawah(user_id: str, position_name: str):
    global pool
    async with pool.acquire() as conn:
        djm_atas = await conn.fetch(
            f'''
            SELECT * 
            FROM "djm_atas_{user_id}" 
            WHERE LOWER(nama_posisi) = LOWER($1)
            ''',
            position_name
        )
        return [dict(record) for record in djm_atas]  # convert ke list of dict

async def retrieve_position(user_id: str, position_name: str):
    global pool
    async with pool.acquire() as conn:
        djm_atas = await conn.fetch(
            f'''
            SELECT * 
            FROM "djm_12_temp_{user_id}" 
            WHERE LOWER(nama_posisi) = LOWER($1)
            ''',
            position_name
        )
        return [dict(record) for record in djm_atas]  # ini aman, djm_atas pasti iterable

