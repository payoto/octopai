import chromadb
from chromadb.config import Settings as ChromaSettings

def get_chroma_client():
    return chromadb.PersistentClient(
        path="./database/chromadb",
        settings=ChromaSettings(
            allow_reset=True,
            is_persistent=True
        )
    )