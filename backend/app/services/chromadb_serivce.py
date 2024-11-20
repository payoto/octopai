from core.database import get_chroma_client
from chromadb.utils import embedding_functions
from core.config import CHROMA_COLLECTION_NAME
import pprint

class ChromaDBService:
    def __init__(self):
        self.default_embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.chroma_client = get_chroma_client()
        self.collection = self.chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            embedding_function=self.default_embedding_function
        )


    def add_documents(self, documents, metadatas=None, ids=None):
        """Add documents to the collection"""
        return self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, query_texts, n_results=5, where=None):
        """Search the collection"""
        return self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )

    def delete(self, ids=None, where=None):
        """Delete documents from collection"""
        return self.collection.delete(
            ids=ids,
            where=where
        )

    def count(self):
        """Get total number of documents"""
        return self.collection.count()

    def peek(self, limit=10):
        """Preview documents in collection"""
        return self.collection.peek(limit=limit)

    def update(self, ids, documents=None, metadatas=None):
        """Update existing documents"""
        return self.collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
    def get_collection(self):
        """Get the collection"""
        return self.collection.get()

    def print_collection(self):
        """Print the collection"""
        result = self.get_collection()
        print(f"Collection {self.collection_name} created successfully")
        pprint.pprint(result)