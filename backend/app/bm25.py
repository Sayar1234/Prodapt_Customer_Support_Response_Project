import re
import json
from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, path):
        with open(path, "r") as f:
            data = json.load(f)

        self.titles = [d["title"] for d in data]
        self.docs = [d["content"] for d in data]

        # ✅ Use class method properly
        self.tokenized = [self.tokenize(doc) for doc in self.docs]

        self.bm25 = BM25Okapi(self.tokenized)

    # ✅ Make it a proper instance method
    def tokenize(self, text):
        return re.findall(r"\w+", text.lower())

    def search(self, query, top_k=5):
        # ✅ Use same tokenizer for query
        tokens = self.tokenize(query)

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )

        # ✅ Normalize scores (important for hybrid)
        max_score = max(scores) if max(scores) > 0 else 1

        results = []
        for idx, score in ranked[:top_k]:
            results.append({
                "title": self.titles[idx],
                "content": self.docs[idx],
                "score": float(score / max_score)  # normalize 0–1
            })

        return results