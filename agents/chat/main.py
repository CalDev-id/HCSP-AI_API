from langchain.tools import Tool
from fastapi import UploadFile
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage
import json
import os
import requests
from main import handle_create_djm
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
from utils import postgredb_apilogy

# --- SESSION MEMORY ---
SESSIONS: Dict[str, Dict] = {}  

from agents.chat.postgres_memory import PostgresConversationMemory

async def get_session_memory(session_id: str) -> PostgresConversationMemory:
    memory = PostgresConversationMemory(session_id=session_id, window=20)
    await memory.load_memory_variables({})
    return memory

# --- TOOLS ---
PROMOTION_MATCH_URL = "http://127.0.0.1:8000/promotion_matching"

def promotion_matching_tool_fn(arg: str) -> str:
    try:
        payload = json.loads(arg)
        resp = requests.post(PROMOTION_MATCH_URL, json=payload, timeout=60)
        return f"[promotion_matching status {resp.status_code}] {resp.text}"
    except Exception as e:
        return f"Error API promotion_matching: {e}"

def return_action_create_djm(_: str) -> str:
    return "create_djm"

TOOLS_FOR_AGENT = [
    Tool(
        name="promotion_matching",
        func=promotion_matching_tool_fn,
        description="Gunakan ini untuk memanggil API promotion matching dengan input JSON string payload kandidat"
    ),
    Tool(
        name="create_djm_selector",
        func=return_action_create_djm,
        description="Pilih ini jika agent ingin membuat DJM. Tool ini hanya mengembalikan string 'create_djm'",
        return_direct=True
    ),

]

# --- LLM & AGENT ---
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def make_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY belum di-set di file .env")

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
        verbose=True,
        agent_kwargs={
            "system_message": SystemMessage(
                content=(
                    "Kamu adalah asisten human capital dalam bahasa Indonesia. "
                    "gunakan tools yang tersedia sesuai kebutuhan. "
                )
        )
    }
    )
    return agent

# AGENT DILUAR AGENT CHAT UTAMA HEHE T_T
async def execute_create_djm(user_id: str, files: Optional[List[UploadFile]]):
    if not files or len(files) == 0:
        return {"error": "Agent ingin membuat DJM, tapi tidak ada file diupload."}

    # mapping berdasarkan ekstensi
    pr_file = next((f for f in files if f.filename.lower().endswith(".pdf")), None)
    template_file = next((f for f in files if f.filename.lower().endswith(".xlsx")), None)

    if not pr_file or not template_file:
        return {
            "error": "Agent ingin membuat DJM, tapi file yang diperlukan tidak lengkap.",
            "needed": {"pr_file": ".pdf", "template_file": ".xlsx"},
            "received": [f.filename for f in files],
        }

    # jalankan handler
    djm_result = await handle_create_djm(user_id, pr_file, template_file)

    if isinstance(djm_result, JSONResponse):
        body = djm_result.body.decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body

    if isinstance(djm_result, dict):
        return djm_result

    return str(djm_result)


async def chat_agent(session_id: str, message: str, files: Optional[List[UploadFile]] = None):
    memory = await get_session_memory(session_id)
    agent = get_agent(memory)

    result = await agent.arun(message)

    # simpan hasil percakapan
    await postgredb_apilogy.insert_chat_message(session_id, "user", message)
    await postgredb_apilogy.insert_chat_message(session_id, "assistant", result)

    ACTION_HANDLERS = {
        "create_djm": lambda: execute_create_djm(session_id, files),
    }

    action = result.strip()
    if action in ACTION_HANDLERS:
        return await ACTION_HANDLERS[action]()

    return result
