from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.bm25 import BM25Retriever
from app.prompts import strict_prompt, friendly_prompt, fallback_prompt
from app.sarvam import call_sarvam
from app.logger import log_request

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = BM25Retriever("app/policies.json")

class QueryRequest(BaseModel):
    query: str
    mode: str

@app.get("/")
def root():
    return {"message": "AI Support Backend Running"}

@app.post("/generate")
def generate(req: QueryRequest):
    results = retriever.search(req.query)

    if results[0]["score"] < 1:
        prompt = fallback_prompt()
        temperature = 0.2
        max_tokens = 50
    else:
        docs_text = "\n\n".join([doc["content"] for doc in results])

        if req.mode == "strict":
            prompt = strict_prompt(docs_text, req.query)
            temperature = 0.2
            max_tokens = 250
        else:
            prompt = friendly_prompt(docs_text, req.query)
            temperature = 0.7
            max_tokens = 250

    response = call_sarvam(prompt, temperature, max_tokens)

    log_request(req.query, results, prompt, temperature, max_tokens)

    return {
        "response": response,
        "documents": results
    }