from pypdf import PdfReader

def load_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"

    return text


def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i + chunk_size]))

    return chunks