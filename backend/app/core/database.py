import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from .config import CHROMA_COLLECTION_NAME


def get_chroma_db_service():
    client = chromadb.PersistentClient(
        path="./database/chromadb",
        settings=ChromaSettings(
            allow_reset=True,
            is_persistent=True
        )
    )
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    )
