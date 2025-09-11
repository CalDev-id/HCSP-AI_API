from chromadb import Client
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

# --- Setup ChromaDB (baru) ---
client = Client(Settings(
    persist_directory="./chroma_db",
    anonymized_telemetry=False
))

collection_name = "pasal_sections"
try:
    collection = client.get_collection(name=collection_name)
except NotFoundError:
    collection = client.create_collection(name=collection_name)

# --- Load embedding model ---
embedding_model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")

# --- Fungsi retrieve dokumen ---
def retrieve_documents(query_text: str, top_k: int = 5):
    """
    Mengambil pasal/section paling relevan dari ChromaDB berdasarkan query_text.
    """
    query_vector = embedding_model.encode(query_text).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    # results['documents'] berbentuk list of list
    return results['documents'][0] if 'documents' in results and results['documents'] else []

# --- ms_agent ---
from LLM.groq_runtime import GroqRunTime

def ms_agent(nama_posisi: str):
    groq_run = GroqRunTime()

    # Ambil pasal/section relevan dari ChromaDB
    data = retrieve_documents(nama_posisi)
    context_text = "\n\n".join(data) if data else "Tidak ada konteks pasal relevan."

    system_prompt = f"""
Peranmu:
Kamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi.

Tugas Utama:
1. Pahami informasi mengenai posisi yang diberikan.
2. pahami antara posisi dan band nya :
- SGM (BAND 1)
- SM  (BAND 2)
- MGR (BAND 3)
- OFF 1 (BAND 4)
- OFF 2/3 (BAND 5/6)

2. Jika posisi dengan BAND (BP) I atau II:
   - Reasoning:
     - Gunakan tools get_context untuk mencari informasi relevan mengenai posisi tersebut.
     - Dari informasi itu, jawab 3 pertanyaan:
       1. Untuk apa posisi ini ada di organisasi?
       2. Apa kontribusi posisi ini kepada organisasi?
       3. Strategi atau unit apa yang didukung oleh posisi ini?
   - Act:
     - Susun jawaban pertanyaan menjadi satu paragraf mission statement.

3. Jika posisi dengan BAND (BP) > II :
   - Reasoning:
     - Pahami posisi dan unitnya.
   - Act:
     - Buat mission statement dengan rumus:
       Mission Statement = “Melakukan pengelolaan fungsi ” + {{nama fungsi}} + “ untuk mendukung pencapaian performansi”

4. Gunakan konteks berikut dari dokumen pasal relevan:
{context_text}

5. Output atau jawaban anda berupa teks bukan list hanya mengandung karakter berupa huruf atau nomor saja.

------------------------------------------------------------

Input:
{nama_posisi}

Mission Statement hanya berupa teks narasi langsung sebutkan misinya tanpa ada kata pengantarnya, tanpa penanda seperti (-/*), dan tidak dibold !
"""

    # Generate response
    response = groq_run.generate_response(system_prompt, nama_posisi)

    if response and hasattr(response.choices[0].message, "content"):
        mission_statement = response.choices[0].message.content.strip()
        print(mission_statement)
        return mission_statement
    else:
        print("Tidak ada respons dari AI.")
        return ""
