import os
import requests
from app.utils import clean_response

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")


def call_openrouter(prompt, temperature=0.7, max_tokens=200):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",  # optional
                "X-Title": "HR Support Bot"
            },
            json={
                "model": "openai/gpt-4o-mini",  # 🔥 default model (fast + cheap)
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )

        data = response.json()

        if "error" in data:
            return f"API Error: {data['error']}"

        raw_text = data["choices"][0]["message"]["content"]

        return clean_response(raw_text)

    except Exception as e:
        return f"API Error: {str(e)}"