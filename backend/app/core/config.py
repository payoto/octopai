import os
from dotenv import load_dotenv

load_dotenv(".env")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CHROMA_USER = os.environ.get("CHROMA_USER")
CHROMA_PASSWORD = os.environ.get("CHROMA_PASSWORD")
CHROMA_COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION_NAME")