from pathlib import Path
from fastapi import FastAPI
from api.chat import router as chat_router
from api.hyde import router as hyde_router
from pipelines.load_documents import load_documents

app = FastAPI()
app.include_router(chat_router)
app.include_router(hyde_router)

if not Path("./database/chromadb/chroma.sqlite3").exists():
    load_documents()