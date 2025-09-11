from chromadb import Client
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

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

def add_section_to_vector_db(section_text: str, section_id: str):
    vector = embedding_model.encode(section_text).tolist()
    collection.add(
        documents=[section_text],
        ids=[section_id],
        embeddings=[vector]
    )

# --- Fungsi retrieve dokumen ---
def retrieve_documents(query_text: str, top_k: int = 5):
    query_vector = embedding_model.encode(query_text).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    # results['documents'] berbentuk list of list
    return results['documents'][0] if 'documents' in results and results['documents'] else []
