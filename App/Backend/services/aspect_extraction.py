import spacy

nlp = spacy.load("en_core_web_sm")


def extract_aspects(text: str, aspects: list[str]) -> list[str]:
    aspects_set = {a.lower() for a in aspects}

    doc = nlp(text)

    detected_aspects = []

    for token in doc:
        if token.lemma_.lower() in aspects_set:
            detected_aspects.append(token.lemma_.lower())

    return detected_aspects