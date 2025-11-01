# app.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv
import os


# --- Load environment variables ---
load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    raise ValueError("Missing ASSEMBLYAI_API_KEY in .env file")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("./app/templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/get_token")
async def get_token():
    url = "https://streaming.assemblyai.com/v3/token"
    params = {"expires_in_seconds": "60"}  # 1–600
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url, params=params, headers={"Authorization": ASSEMBLYAI_API_KEY}
        )
    if r.status_code != 200:
        return {"error": f"Failed to get token: {r.status_code} {r.text}"}
    return r.json()
