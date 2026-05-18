import torch
import numpy as np
from scipy.special import softmax

from services.preprocessing import preprocess_text, split_into_phrases
from services.model_loader import load_sentiment_model, LABELS
from services.aspect_extraction import extract_aspects


# Empty container — will be filled at startup
model_state = {
    "tokenizer": None,
    "model": None,
}


def load_model():
    tokenizer, model = load_sentiment_model()
    model.eval()

    model_state["tokenizer"] = tokenizer
    model_state["model"] = model


def predict_batch(texts: list[str]) -> list[dict]:
    tokenizer = model_state["tokenizer"]
    model = model_state["model"]

    cleaned_texts = [preprocess_text(text) for text in texts]

    encoded_input = tokenizer(
        cleaned_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )

    with torch.no_grad():
        output = model(**encoded_input)

    scores = softmax(output.logits.detach().numpy(), axis=1)

    results = []

    for score in scores:
        predicted_class = int(np.argmax(score))

        results.append({
            "label": LABELS[predicted_class],
            "score": round(float(score[predicted_class]), 2)
        })

    return results


def predict_comments(comments: list[str]) -> dict:
    aspect_results = []
    without_aspect_results = []
    all_phrases = []

    for comment in comments:
        clean_comment = preprocess_text(comment)
        phrases = split_into_phrases(clean_comment)
        all_phrases.extend(phrases)

    if not all_phrases:
        return {
            "aspect_analysis": [],
            "without_aspect_analysis": []
        }

    predictions = predict_batch(all_phrases)

    for phrase, prediction in zip(all_phrases, predictions):
        aspects = extract_aspects(phrase)

        if aspects:
            for aspect in aspects:
                aspect_results.append({
                    "phrase": phrase,
                    "aspect": aspect,
                    "label": prediction["label"],
                    "score": prediction["score"]
                })
        else:
            without_aspect_results.append({
                "phrase": phrase,
                "label": prediction["label"],
                "score": prediction["score"]
            })

    return {
        "aspect_analysis": aspect_results,
        "without_aspect_analysis": without_aspect_results
    }