from llm.groq_runtime import GroqRunTime
from fastapi import FastAPI, UploadFile, File
from agents.djm.djm import handle_create_djm
from agents.chat.main import chat_agent

#uvicorn main:app --reload

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "welcome to the HCSP-AI API"}


@app.post("/create_djm")
async def create_djm(
    pr_file: UploadFile = File(..., description="Upload a PDF file"),
    template_file: UploadFile = File(..., description="Upload an XLSX file")
):
    return await handle_create_djm(pr_file, template_file)

@app.post("/chat")
def chat_endpoint(user_prompt: str):
    response = chat_agent(user_prompt)
    return {"response": response}