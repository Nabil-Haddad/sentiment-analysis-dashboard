import torch
import numpy as np
from scipy.special import softmax

from preprocessing import preprocess_text, split_into_phrases
from model_loader import load_sentiment_model, get_labels
from aspect_extraction import extract_aspects


tokenizer, model = load_sentiment_model()
labels = get_labels()


def predict_sentiment(text: str) -> dict:
    cleaned_text = preprocess_text(text)

    encoded_input = tokenizer(
        cleaned_text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        output = model(**encoded_input)

    scores = softmax(output.logits.detach().numpy()[0])
    predicted_class = np.argmax(scores)

    return {
        "Label": labels[predicted_class],
        "Score": round(float(scores[predicted_class]), 2)
    }


def predict_batch(texts: list[str]) -> list[dict]:
    texts = [preprocess_text(t) for t in texts]

    encoded_input = tokenizer(
        texts,
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
        predicted_class = np.argmax(score)

        results.append({
            "Label": labels[predicted_class],
            "Score": round(float(score[predicted_class]), 2)
        })

    return results


def aspect_based_sentiment(comments: list[str]) -> dict:
    results_with_aspects = []
    results_without_aspects = []

    all_phrases = []

    for comment in comments:
        phrases = split_into_phrases(comment)
        all_phrases.extend(phrases)

    predictions = predict_batch(all_phrases)

    for phrase, pred in zip(all_phrases, predictions):
        aspects = extract_aspects(phrase)

        if aspects:
            results_with_aspects.append({
                "Phrase": phrase,
                "Aspects": aspects,
                "Label": pred["Label"],
                "Score": pred["Score"]
            })
        else:
            results_without_aspects.append({
                "Phrase": phrase,
                "Label": pred["Label"],
                "Score": pred["Score"]
            })

    return {
        "with_aspects": results_with_aspects,
        "without_aspects": results_without_aspects
    }