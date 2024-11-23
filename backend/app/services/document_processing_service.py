import os

from ..core.database import get_chroma_db_service

class DocumentProcessor:
    def __init__(self):
        """Initialize DocumentProcessor"""
        self.db = get_chroma_db_service()

    def load_txt_from_dir(self) -> list:
        documents_path = "./database/documents"
        documents = []
        for filename in os.listdir(documents_path):
            if filename.endswith(".md"):
                with open(os.path.join(documents_path, filename), "r") as file:
                    documents.append({"text": file.read()})
        return documents

    def split_text(self, text,
                   chunk_size=256,
                   chunk_overlap=20):
        chunks = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - chunk_overlap
        return chunks

    def process_documents(self, documents: list) -> list:
        """Process documents."""
        chunked_txt = []

        for file_id, txt_file in enumerate(documents):
            chunks = self.split_text(txt_file["text"])
            for chunk_id, chunk in enumerate(chunks):
                chunked_txt.append(
                    {
                        'id': f"{file_id}-{chunk_id}",
                        'text': chunk,
                    }
                )
        return chunked_txt


    def add_documents_to_db(self, chunked_txt: list):
        """Add documents to database."""
        for chunk in chunked_txt :
            self.db.upsert(
                    ids=chunk['id'],
                    documents=chunk['text'],
            )