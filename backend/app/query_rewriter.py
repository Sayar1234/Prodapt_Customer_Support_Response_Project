from app.openrouter import call_openrouter


def rewrite_query(query: str) -> str:
    prompt = f"""
You are a query expansion system for HR policy search.

Your job:
- Expand the query with relevant HR/legal keywords
- Add synonyms and related terms
- Improve retrieval recall for a hybrid search system (BM25 + vector DB)

Rules:
- Do NOT answer the question
- Keep it under 20 words
- Keep it as a single search query string

User Query:
{query}

Expanded Query:
"""

    rewritten = call_openrouter(
        prompt=prompt,
        temperature=0.2,
        max_tokens=60
    )

    # safety fallback
    if not rewritten or len(rewritten.strip()) == 0:
        return query

    return rewritten.strip()