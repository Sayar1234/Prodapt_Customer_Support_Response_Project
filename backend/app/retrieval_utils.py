def normalize_docs(results):
    normalized = []

    for r in results:
        content = (
            r.get("content")
            or r.get("text")
            or r.get("metadata", {}).get("text")
            or ""
        )

        title = (
            r.get("title")
            or r.get("metadata", {}).get("source")
            or "Policy Document"
        )

        normalized.append({
            "content": content.strip(),
            "title": title,
            "score": float(r.get("score", 0))
        })

    return normalized


def deduplicate_docs(docs):
    seen = set()
    unique_docs = []

    for d in docs:
        key = d["content"][:200]  # partial match to avoid full duplicates

        if key not in seen and d["content"]:
            seen.add(key)
            unique_docs.append(d)

    return unique_docs


def build_context(docs, max_chars=3000):
    context = []
    total = 0

    for d in docs:
        text = d["content"]

        if total + len(text) > max_chars:
            break

        context.append(text)
        total += len(text)

    return "\n\n".join(context)