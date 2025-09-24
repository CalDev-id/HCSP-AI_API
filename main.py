from llm.groq_runtime import GroqRunTime
from agents.djm.band_atas.djm import handle_create_djm
from agents.djm.band_bawah.djm import handle_create_djm_bawah
from agents.chat.main import chat_agent
from utils import postgredb_apilogy
from contextlib import asynccontextmanager
from pydantic import BaseModel
from fastapi import FastAPI, Form, File, UploadFile, Body
from typing import Optional
from typing import Dict, Any, Union, List


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
user_id = "cal31"

@app.get("/")
def read_root():
    return {"message": "welcome to the HCSP-AI API"}


@app.post("/create_djm_atas")
async def create_djm(
    user_id: str = Form(..., description="User ID"),
    pr_file: UploadFile = File(..., description="Upload a PDF file"),
    template_file: UploadFile = File(..., description="Upload a XLSX template file")
):
    return await handle_create_djm(user_id, pr_file, template_file)

class DJMData(BaseModel):
    jobId: int
    nama_posisi: str
    mission_statement: str
    job_responsibilities: str
    job_performance: str
    job_authorities: str

class DJMRequest(BaseModel):
    user_id: str
    data: List[DJMData]

@app.post("/create_djm_bawah")
async def create_djm_bawah(request: DJMRequest):
    return await handle_create_djm_bawah(request.user_id, request.data)

@app.post("/chat")
async def chat_endpoint(
    session_id: str = Form(...),
    message: str = Form(...),
    file: Optional[UploadFile] = None
):
    response = await chat_agent(session_id, message, file)
    return response

@app.post("/retrieve_position")
async def retrieve_position_endpoint(position_name: str = Body(..., embed=True)):
    try:
        djm_atas = await postgredb_apilogy.retrieve_position(user_id, position_name)
        results = [dict(record) for record in djm_atas]
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}


#======================================================
# from llm.groq_runtime import GroqRunTime
# from agents.djm.djm import handle_create_djm
# from agents.chat.main import chat_agent
# from utils import postgredb_apilogy
# from contextlib import asynccontextmanager
# from pydantic import BaseModel
# from fastapi import FastAPI, Form, File, UploadFile
# from typing import Optional
# from typing import List


# #uvicorn main:app --reload

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await postgredb_apilogy.init_db_pool()
#     print("Database pool initialized.")
#     yield
#     if postgredb_apilogy.pool:
#         await postgredb_apilogy.pool.close()
#         print("Database pool closed.")


# app = FastAPI(lifespan=lifespan)

# @app.get("/")
# def read_root():
#     return {"message": "welcome to the HCSP-AI API"}


# @app.post("/create_djm")
# async def create_djm(
#     pr_file: List[UploadFile] = File(..., description="Upload a PDF file"),
#     template_file: UploadFile = File(..., description="Upload a XLSX template file")
# ):
#     return await handle_create_djm(pr_file, template_file)

# @app.post("/chat")
# async def chat_endpoint(
#     session_id: str = Form(...),
#     message: str = Form(...),
#     file: Optional[UploadFile] = None
# ):
#     response = await chat_agent(session_id, message, file)
#     return response
