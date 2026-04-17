import re

def clean_response(text: str) -> str:
    if not text:
        return "No response generated"

    # Remove numbered reasoning patterns
    text = re.sub(r"\d+\.\s\*\*.*?\*\*", "", text)

    # Remove "Step 1 / Step 2" patterns
    text = re.sub(r"Step \d+.*?:", "", text)

    # Remove markdown bold headers
    text = re.sub(r"\*\*.*?\*\*", "", text)

    # Remove extra whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text