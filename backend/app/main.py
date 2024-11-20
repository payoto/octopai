from fastapi import FastAPI
from api.chat import router as chat_router
from api.hyde import router as hyde_router

app = FastAPI()
app.include_router(chat_router)
app.include_router(hyde_router)
