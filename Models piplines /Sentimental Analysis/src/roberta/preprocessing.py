import re


def preprocess_text(text: str) -> str:

    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")

    text = re.sub(r"@\w+", "@user", text)
    text = re.sub(r"http\S+|www\S+", "http", text)

    return text.strip()



def split_into_phrases(text: str) -> list[str]:
    parts = re.split(r"\s*(?:\.|\bbut\b|\bhowever\b)\s*",text,flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]