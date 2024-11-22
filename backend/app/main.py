from pathlib import Path
from fastapi import FastAPI
from api.chat import router as chat_router
from api.hyde import router as hyde_router
from api.meeting import router as meeting_router
from pipelines.load_documents import load_documents
from core.context import request_context_manager
import uuid
import datetime

app = FastAPI()

@app.middleware("http")
async def context_middleware(request, call_next):
    with request_context_manager() as context:
        # Set context values from request
        context.set_request_id(f"{datetime.datetime.now().isoformat()}_{uuid.uuid1().hex[:4]}")
        response = await call_next(request)
        return response

app.include_router(chat_router)
app.include_router(hyde_router)
app.include_router(meeting_router)

if not Path("./database/chromadb/chroma.sqlite3").exists():
    load_documents()