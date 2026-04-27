import re
from rank_bm25 import BM25Okapi

from app.pdf_loader import load_pdf, chunk_text


class BM25Retriever:
    def __init__(self, pdf_path):
        # 1. Load PDF text
        text = load_pdf(pdf_path)

        # 2. Chunk it (same as Pinecone → consistency is key)
        self.docs = chunk_text(text)

        # 3. Tokenize chunks
        self.tokenized = [self.tokenize(doc) for doc in self.docs]

        # 4. Build BM25 index
        self.bm25 = BM25Okapi(self.tokenized)

    def tokenize(self, text):
        return re.findall(r"\w+", text.lower())

    def search(self, query, top_k=5):
        tokens = self.tokenize(query)

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )

        max_score = max(scores) if max(scores) > 0 else 1

        results = []
        for idx, score in ranked[:top_k]:
            results.append({
                "title": "HR Policy",   # or extract heading later
                "content": self.docs[idx],
                "score": float(score / max_score)
            })

        return results