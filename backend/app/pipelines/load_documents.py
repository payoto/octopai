from services.document_processing_service import DocumentProcessor
from core.database import get_chroma_db_service

def load_documents():
    """Load documents."""
    processor = DocumentProcessor()
    db = get_chroma_db_service()
    documents = processor.load_txt_from_dir()
    chunked_txt = processor.process_documents(documents)
    processor.add_documents_to_db(chunked_txt)
    print(db)
    return print("Documents loaded successfully.")