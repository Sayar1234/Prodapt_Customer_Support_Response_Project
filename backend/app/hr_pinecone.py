import os
import uuid
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

from app.pdf_loader import load_pdf, chunk_text


class HRPineconeRetriever:
    def __init__(self, pdf_path):
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX", "hr-policy")

        if not api_key:
            raise ValueError("Missing PINECONE_API_KEY")

        # Init Pinecone
        self.pc = Pinecone(api_key=api_key)

        self.index_name = index_name

        # Create index if not exists
        if index_name not in [i["name"] for i in self.pc.list_indexes()]:
            self.pc.create_index(
                name=index_name,
                dimension=384,  # MiniLM embedding size
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        self.index = self.pc.Index(index_name)

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Check if index is empty
        stats = self.index.describe_index_stats()
        if stats["total_vector_count"] == 0:
            self._index(pdf_path)

    def _index(self, pdf_path):
        text = load_pdf(pdf_path)
        chunks = chunk_text(text)

        embeddings = self.embedder.encode(chunks).tolist()

        vectors = []
        for i, chunk in enumerate(chunks):
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embeddings[i],
                "metadata": {
                    "text": chunk,
                    "source": "sample.pdf"
                }
            })

        # Upsert in batches (important for Pinecone)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            self.index.upsert(vectors=vectors[i:i + batch_size])

    def search(self, query, top_k=3):
        q_emb = self.embedder.encode([query])[0].tolist()

        res = self.index.query(
            vector=q_emb,
            top_k=top_k,
            include_metadata=True
        )

        return [
            {
                "title": "HR Policy",
                "content": match["metadata"]["text"]
            }
            for match in res["matches"]
        ]