import asyncpg
from typing import Optional
from utils.embedding import get_embedding
import json
from typing import List, Dict, Any
from llm.apilogy_runtime import ApilogyRunTime

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
                id SERIAL PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding vector(768)
            );
        ''')
    return table_name

async def add_section(user_id: str, section_text: str, metadata):
    global pool
    table_name = f"data_pr_{user_id}"

    cleaned_text = section_text.replace("\n", " ").replace("'", "")

    if isinstance(metadata, str):
        metadata = {"pasalTitle": metadata}

    metadata_str = json.dumps(metadata, ensure_ascii=False)

    vector = get_embedding(section_text)
    vector_str = "[" + ",".join(str(x) for x in vector) + "]"

    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO "{table_name}" (content, metadata, embedding)
            VALUES ($1, $2::jsonb, $3::vector);
            """,
            cleaned_text, metadata_str, vector_str
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

    contents = [row["content"] for row in rows if row["content"]]

    combined_text = " ".join(
        [f"Chunk {i+1}: {c}" for i, c in enumerate(contents)]
    )

    return combined_text

async def retrieve_position_bawah(user_id: str, position_name: str):
    global pool
    async with pool.acquire() as conn:
        djm_atas = await conn.fetch(
            f'''
            SELECT * 
            FROM "djm_verified_{user_id}" 
            WHERE LOWER(nama_posisi) = LOWER($1)
            ''',
            position_name
        )
        return [dict(record) for record in djm_atas]

async def retrieve_position(user_id: str, position_name: str):
    global pool
    async with pool.acquire() as conn:
        djm_atas = await conn.fetch(
            f'''
            SELECT * 
            FROM "djm_temp_{user_id}" 
            WHERE LOWER(nama_posisi) = LOWER($1)
            ''',
            position_name
        )
        return [dict(record) for record in djm_atas]



#chat
async def ensure_chat_table_exists():
    """Buat table chat_history kalau belum ada."""
    global pool
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)


async def insert_chat_message(session_id: str, role: str, message: str):
    """Simpan pesan user/assistant ke PostgreSQL."""
    global pool
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO chat_history (session_id, role, message) VALUES ($1, $2, $3)",
            session_id, role, message
        )


async def fetch_chat_history(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Ambil N chat terakhir berdasarkan session_id (urut awal → akhir)."""
    global pool
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, message, created_at
            FROM chat_history
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            session_id, limit
        )
        return list(reversed([dict(r) for r in rows]))
    

def cari_database(nama_posisi, metadata_dict):
    apilogy_run = ApilogyRunTime()

    def ambil_ringkasan_pasal(title):
        if not title:
            return ""

        title = str(title).replace('"', '').replace("'", "").strip()

        if "." in title:
            first_sentence = title.split(".")[0].strip()
        else:
            first_sentence = " ".join(title.split()[:20]).strip()

        return first_sentence

    metadata_text = "\n".join([
        f"Sumber ID : {mid} || Sumber pasal : {ambil_ringkasan_pasal(meta.get('pasalTitle', '')) if isinstance(meta, dict) else ambil_ringkasan_pasal(meta)}"
        for mid, meta in metadata_dict.items()
    ])

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

