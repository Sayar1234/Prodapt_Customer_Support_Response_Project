from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from app.prompts import strict_prompt, friendly_prompt, fallback_prompt
# from app.sarvam import call_sarvam
from app.openrouter import call_openrouter
from app.logger import log_request

from app.hr_pinecone import HRPineconeRetriever
from app.bm25 import BM25Retriever
from app.retrieval_utils import normalize_docs, deduplicate_docs, build_context
from app.reranker import Reranker
from app.query_rewriter import rewrite_query

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Initialize retrievers
# bm25 = BM25Retriever("app/policies.json")
bm25 = BM25Retriever("app/sample.pdf")
pinecone = HRPineconeRetriever("app/sample.pdf")
reranker = Reranker()


class QueryRequest(BaseModel):
    query: str
    mode: str


@app.get("/")
def root():
    return {"message": "AI HR Support Backend Running"}


@app.post("/generate")
def generate(req: QueryRequest):
    # query = req.query.strip()
    original_query = req.query.strip()
    query = rewrite_query(original_query)

    # 🔹 1. Hybrid Retrieval
    pinecone_results = pinecone.search(query, top_k=10)
    bm25_results = bm25.search(query, top_k=10)

    # 🔹 2. Normalize (safe even if already clean)
    pinecone_results = normalize_docs(pinecone_results)
    bm25_results = normalize_docs(bm25_results)

    # 🔹 3. Score weighting (IMPORTANT)
    for d in pinecone_results:
        d["score"] *= 1.2  # semantic boost

    for d in bm25_results:
        d["score"] *= 0.8  # keyword lower weight

    # 🔹 4. Merge
    results = pinecone_results + bm25_results

    # 🔹 5. Deduplicate
    results = deduplicate_docs(results)

    # 🔹 6. Rerank
    if results:
        results = reranker.rerank(query, results, top_n=5)

    # 🔹 DEBUG (remove later if needed)
    print("\n=== FINAL RETRIEVED DOCS ===")
    for i, d in enumerate(results):
        print(f"{i+1}. {d['title']} | {d['score']:.3f}")
        print(d["content"][:120])
        print("------")

    # 🔹 7. Fallback check
    if not results or results[0]["score"] < 0.15:
        prompt = fallback_prompt()
        temperature = 0.2
        max_tokens = 80
    else:
        docs_text = build_context(results)

        if req.mode == "strict":
            prompt = strict_prompt(docs_text, query)
            temperature = 0.2
        else:
            prompt = friendly_prompt(docs_text, query)
            temperature = 0.7

        max_tokens = 250

    # 🔹 8. LLM call
    response = call_openrouter(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        # model="openai/gpt-4o-mini"
    )

    # 🔹 9. Logging
    log_request(query, results, prompt, temperature, max_tokens)

    # 🔹 10. Response
    return {
        "response": response,
        "documents": [
            {
                "id": f"doc-{i}",
                "title": d["title"],
                "content": d["content"],
                "score": round(d["score"], 3),
                "preview": d["content"][:180] + "..."
            }
            for i, d in enumerate(results)
        ]
    }