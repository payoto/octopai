from fastapi import FastAPI
from api.chat import router as chat_router
from api.hyde import router as hyde_router
from pipelines.load_documents import load_documents

app = FastAPI()
app.include_router(chat_router)
app.include_router(hyde_router)

load_documents()