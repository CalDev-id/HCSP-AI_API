from langchain.tools import Tool
from fastapi import UploadFile
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
import json
import os
import requests
from main import handle_create_djm
from fastapi.responses import JSONResponse
from typing import Optional, Dict

# --- SESSION MEMORY ---
SESSIONS: Dict[str, Dict] = {}  

def get_session_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {"memory": ConversationBufferMemory(memory_key="chat_history")}
    return SESSIONS[session_id]["memory"]

# --- TOOLS ---
PROMOTION_MATCH_URL = "http://127.0.0.1:8000/promotion_matching"

def promotion_matching_tool_fn(arg: str) -> str:
    """Tool untuk memanggil promotion_matching API"""
    try:
        payload = json.loads(arg)
        resp = requests.post(PROMOTION_MATCH_URL, json=payload, timeout=60)
        return f"[promotion_matching status {resp.status_code}] {resp.text}"
    except Exception as e:
        return f"Error API promotion_matching: {e}"

def create_djm_selector_tool_fn(_: str) -> str:
    """Tool yang dipilih agent, hanya mengembalikan 'create_djm'"""
    return "create_djm"

TOOLS_FOR_AGENT = [
    Tool(
        name="promotion_matching",
        func=promotion_matching_tool_fn,
        description="Gunakan ini untuk memanggil API promotion matching dengan input JSON string payload kandidat"
    ),
    Tool(
        name="create_djm_selector",
        func=create_djm_selector_tool_fn,
        description="Pilih ini jika agent ingin membuat DJM. Tool ini hanya mengembalikan string 'create_djm'",
        return_direct=True
    ),

]

# --- LLM & AGENT ---
API_KEY_PATH = "config/secrets/api_key.txt"
if not os.path.exists(API_KEY_PATH):
    raise FileNotFoundError(f"Buat file {API_KEY_PATH} yang berisi GROQ API key Anda")
with open(API_KEY_PATH, "r") as f:
    os.environ["GROQ_API_KEY"] = f.read().strip()


def make_llm():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY belum di-set dari file.")
    
    return ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=1024
    )

def get_agent(memory: ConversationBufferMemory):
    llm = make_llm()
    agent = initialize_agent(
        TOOLS_FOR_AGENT,
        llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )
    return agent

# AGENT DILUAR AGENT CHAT UTAMA HEHE T_T
async def execute_create_djm(file: Optional[UploadFile]):
    """Eksekusi action create_djm dengan file."""
    if not file:
        return {"error": "Agent ingin membuat DJM, tapi tidak ada file diupload."}

    djm_result = await handle_create_djm(file)

    if isinstance(djm_result, JSONResponse):
        body = djm_result.body.decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body

    if isinstance(djm_result, dict):
        return djm_result

    return str(djm_result)


async def chat_agent(session_id: str, message: str, file: Optional[UploadFile] = None):
    memory = get_session_memory(session_id)
    agent = get_agent(memory)

    result = agent.run(message)

    ACTION_HANDLERS = {
        "create_djm": lambda: execute_create_djm(file),
    }

    action = result.strip()
    if action in ACTION_HANDLERS:
        return await ACTION_HANDLERS[action]()

    return result
