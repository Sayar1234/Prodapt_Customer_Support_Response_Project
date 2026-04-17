import json
from datetime import datetime

def log_request(query, docs, prompt, temp, tokens):
    log = {
        "timestamp": str(datetime.now()),
        "query": query,
        "docs": docs,
        "temperature": temp,
        "max_tokens": tokens
    }

    with open("logs.json", "a") as f:
        f.write(json.dumps(log) + "\n")