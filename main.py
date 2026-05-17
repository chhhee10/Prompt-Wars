from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

from parser import extract_text
from agents.pipeline import analyze_document

app = FastAPI(title="LEXGUARD API")

class AnalyzeRequest(BaseModel):
    document: str
    language: Optional[str] = "en"
    document_type: Optional[str] = None

# Ensure static dir exists for phase 3 UI
os.makedirs("static", exist_ok=True)
if not os.path.exists("static/index.html"):
    with open("static/index.html", "w") as f:
        f.write("<html><body><h1>Lexguard UI Coming Soon</h1></body></html>")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        text = extract_text(req.document)
        result = analyze_document(text, language=req.language)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Mount static files at the root directory (so /assets, /gavel.png, and / work!)
# Placed at the bottom so API routes take precedence
app.mount("/", StaticFiles(directory="static", html=True), name="static")
