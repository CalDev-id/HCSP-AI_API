# import asyncpg
# from sentence_transformers import SentenceTransformer

# # --- Load embedding model ---
# embedding_model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")

# DB_URL = "postgresql://cal:pass@localhost:5432/cal"
# from typing import Optional
# pool: Optional[asyncpg.pool.Pool] = None


# # --- Inisialisasi pool sekali di startup ---
# async def init_db_pool():
#     global pool
#     pool = await asyncpg.create_pool(DB_URL)
#     print("✅ Database pool initialized")

# # --- Fungsi tambah section ke DB ---
# async def add_section_to_vector_db(section_text: str, section_id: str):
#     global pool
#     if pool is None:
#         raise RuntimeError("Database pool is not initialized. Call init_db_pool() first.")

#     vector = embedding_model.encode(section_text).tolist()
#     vector_str = "[" + ",".join(str(x) for x in vector) + "]"

#     async with pool.acquire() as conn:
#         await conn.execute(
#             """
#             INSERT INTO pasal_sections (id, content, embedding)
#             VALUES ($1, $2, $3::vector)
#             ON CONFLICT (id) DO UPDATE
#             SET content = EXCLUDED.content,
#                 embedding = EXCLUDED.embedding;
#             """,
#             section_id, section_text, vector_str
#         )

# # --- Fungsi retrieve dokumen ---
# async def retrieve_documents(query_text: str, top_k: int = 5):
#     global pool
#     if pool is None:
#         raise RuntimeError("Database pool is not initialized. Call init_db_pool() first.")

#     query_vector = embedding_model.encode(query_text).tolist()
#     query_vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

#     async with pool.acquire() as conn:
#         rows = await conn.fetch(
#             """
#             SELECT content
#             FROM pasal_sections
#             ORDER BY embedding <-> $1::vector
#             LIMIT $2;
#             """,
#             query_vector_str, top_k
#         )

#     return [row["content"] for row in rows]


import asyncpg
from sentence_transformers import SentenceTransformer
from typing import Optional

embedding_model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")
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
                embedding vector(768)
            );
        ''')

    return table_name

async def add_section(user_id: str, section_text: str, section_id: str):
    global pool
    table_name = f"data_pr_{user_id}"
    vector = embedding_model.encode(section_text).tolist()
    vector_str = "[" + ",".join(str(x) for x in vector) + "]"

    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO "{table_name}" (id, content, embedding)
            VALUES ($1, $2, $3::vector)
            ON CONFLICT (id) DO UPDATE
            SET content = EXCLUDED.content,
                embedding = EXCLUDED.embedding;
            """,
            section_id, section_text, vector_str
        )

async def retrieve_documents(user_id: str, query_text: str, top_k: int = 5):
    global pool
    table_name = f"data_pr_{user_id}"
    query_vector = embedding_model.encode(query_text).tolist()
    query_vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT content
            FROM "{table_name}"
            ORDER BY embedding <-> $1::vector
            LIMIT $2;
            """,
            query_vector_str, top_k
        )

    return [row["content"] for row in rows]

async def drop_user_table(user_id: str):
    global pool
    table_name = f"data_pr_{user_id}"
    async with pool.acquire() as conn:
        await conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')

