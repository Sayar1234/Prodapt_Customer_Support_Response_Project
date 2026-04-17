import json
from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, path):
        with open(path, "r") as f:
            data = json.load(f)

        self.titles = [d["title"] for d in data]
        self.docs = [d["content"] for d in data]

        self.tokenized = [doc.lower().split() for doc in self.docs]
        self.bm25 = BM25Okapi(self.tokenized)

    def search(self, query, top_k=3):
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_k]:
            results.append({
                "title": self.titles[idx],
                "content": self.docs[idx],
                "score": float(score)
            })

        return results