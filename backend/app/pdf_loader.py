from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"

    return text

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=75,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    return splitter.split_text(text)