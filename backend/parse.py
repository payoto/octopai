# bring in our LLAMA_CLOUD_API_KEY
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv()

# bring in deps
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# set up parser
parser = LlamaParse(
    result_type="markdown",  # "markdown" and "text" are available
    # use_vendor_multimodal_model=True,
    # vendor_multimodal_model_name="anthropic-sonnet-3.5",
    # vendor_multimodal_api_key=ANTHROPIC_API_KEY,

)

# use SimpleDirectoryReader to parse our file
def extract_pdf(path, db_path):
    file_extractor = {".pdf": parser}
    print("Extracting files")
    documents = SimpleDirectoryReader(input_files=[str(path)], file_extractor=file_extractor).load_data()

    for idx, i in enumerate(documents):
        print("Writing files")
        file_name = documents[idx].metadata["file_name"].split(".")[0] + ".md"
        file_path = db_path / file_name
        file_path.write_text(documents[idx].text)


pdf_folder = Path("pdfs")
md_folder = Path("database/documents")

pdf_files = list(pdf_folder.glob("*.pdf"))
md_files = list(md_folder.glob("*.md"))
converted_files = {md.stem for md in md_files}
for pdf in pdf_files:
    if pdf.stem not in converted_files:
        extract_pdf(pdf, md_folder)
    else:
        print("No files to extract")
