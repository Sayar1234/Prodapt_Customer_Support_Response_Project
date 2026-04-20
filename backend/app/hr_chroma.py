import chromadb
from sentence_transformers import SentenceTransformer
from app.pdf_loader import load_pdf, chunk_text
import uuid

class HRChromaRetriever:
    def __init__(self, pdf_path):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("hr_policy")

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        if self.collection.count() == 0:
            self._index(pdf_path)

    def _index(self, pdf_path):
        text = load_pdf(pdf_path)
        chunks = chunk_text(text)

        embeddings = self.embedder.encode(chunks).tolist()

        self.collection.add(
            ids=[str(uuid.uuid4()) for _ in chunks],
            documents=chunks,
            embeddings=embeddings,
            metadatas=[{"source": "sample.pdf"} for _ in chunks]
        )

    def search(self, query, top_k=3):
        q_emb = self.embedder.encode([query]).tolist()

        res = self.collection.query(
            query_embeddings=q_emb,
            n_results=top_k
        )

        return [
            {
                "title": "HR Policy",
                "content": res["documents"][0][i]
            }
            for i in range(len(res["documents"][0]))
        ]