from llm.groq_runtime import GroqRunTime
from agents.djm.djm import handle_create_djm
from agents.chat.main import chat_agent
from utils import postgredb_apilogy
from contextlib import asynccontextmanager
from pydantic import BaseModel
from fastapi import FastAPI, Form, File, UploadFile
from typing import Optional


#uvicorn main:app --reload

@asynccontextmanager
async def lifespan(app: FastAPI):
    await postgredb_apilogy.init_db_pool()
    print("Database pool initialized.")
    yield
    if postgredb_apilogy.pool:
        await postgredb_apilogy.pool.close()
        print("Database pool closed.")


app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "welcome to the HCSP-AI API"}


@app.post("/create_djm")
async def create_djm(
    pr_file: UploadFile = File(..., description="Upload a PDF file"),
):
    return await handle_create_djm(pr_file)

@app.post("/chat")
async def chat_endpoint(
    session_id: str = Form(...),
    message: str = Form(...),
    file: Optional[UploadFile] = None
):
    response = await chat_agent(session_id, message, file)
    return response
