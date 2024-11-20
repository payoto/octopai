from services.document_processing_service import DocumentProcessor
from services.chromadb_serivce import ChromaDBService

def load_documents():
    """Load documents."""
    processor = DocumentProcessor()
    db = ChromaDBService()
    documents = processor.load_txt_from_dir()
    chunked_txt = processor.process_documents(documents)
    processor.add_documents_to_db(chunked_txt)
    print(db.get_collection())
    return print("Documents loaded successfully.")