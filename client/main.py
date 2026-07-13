from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from client import run_agent
from schemas import ChatRequest
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Event Ticketing AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_BASE_URL")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = await run_agent(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))