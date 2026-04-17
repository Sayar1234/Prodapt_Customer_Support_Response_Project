from dotenv import load_dotenv
load_dotenv()

import os
from sarvamai import SarvamAI
from app.utils import clean_response

# Create client once (better performance)
def get_client():
    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise ValueError("SARVAM_API_KEY missing in environment")

    return SarvamAI(api_subscription_key=api_key)


client = get_client()


def call_sarvam(prompt, temperature=0.7, max_tokens=200):
    try:
        response = client.chat.completions(
            model="sarvam-105b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        print("SARVAM RAW RESPONSE:", response)

        msg = response.choices[0].message

        # 🔥 robust extraction (covers all SDK behaviors)
        raw_text = (
            msg.content
            or getattr(msg, "reasoning_content", None)
            or ""
        )

        if not raw_text:
            return "No response generated"

        # 🧹 clean reasoning / junk formatting
        return clean_response(raw_text)

    except Exception as e:
        return f"API Error: {str(e)}"