import torch
import numpy as np
from scipy.special import softmax

from services.preprocessing import preprocess_text, split_into_phrases
from services.model_loader import load_sentiment_model, load_absa_model, LABELS
from services.aspect_extraction import extract_aspects
from core.config import SENTIMENT_BACKEND


model_state = {
    "tokenizer": None,
    "model":     None,
    "device":    None,
    "backend":   None,
}


def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if SENTIMENT_BACKEND == "deberta_absa":
        print("Loading fine-tuned DeBERTa ABSA model (paid tier)...")
        tokenizer, model = load_absa_model()
    else:
        print("Loading cardiffnlp RoBERTa model (free tier)...")
        tokenizer, model = load_sentiment_model()

    model.to(device)
    model.eval()

    model_state["tokenizer"] = tokenizer
    model_state["model"]     = model
    model_state["device"]    = device
    model_state["backend"]   = SENTIMENT_BACKEND

    print(f"Model ready — backend: {SENTIMENT_BACKEND} | device: {device}")


def build_absa_input(text: str, aspect: str) -> str:
    return f"aspect: {aspect} [SEP] {text}"




def predict_batch_roberta(texts: list[str]) -> list[dict]:
    tokenizer = model_state["tokenizer"]
    model     = model_state["model"]

    cleaned_texts = [preprocess_text(text) for text in texts]

    encoded_input = tokenizer(
        cleaned_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )

    with torch.no_grad():
        output = model(**encoded_input)

    scores  = softmax(output.logits.detach().numpy(), axis=1)
    results = []

    for score in scores:
        predicted_class = int(np.argmax(score))
        results.append({
            "label": LABELS[predicted_class],
            "score": round(float(score[predicted_class]), 2),
        })

    return results


def predict_batch_absa(pairs: list[dict]) -> list[dict]:

    tokenizer = model_state["tokenizer"]
    model     = model_state["model"]
    device    = model_state["device"]

    input_texts = [
        build_absa_input(pair["text"], pair["aspect"])
        for pair in pairs
    ]

    encoded = tokenizer(
        input_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )

    input_ids      = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    scores  = softmax(outputs.logits.cpu().detach().numpy(), axis=1)
    results = []

    for score in scores:
        predicted_class = int(np.argmax(score))
        results.append({
            "label": LABELS[predicted_class],
            "score": round(float(score[predicted_class]), 2),
        })

    return results




# RoBERTa pipeline
def _predict_comments_roberta(comments: list[str], active_aspects: list[str]) -> dict:
    aspect_results         = []
    without_aspect_results = []
    all_phrases            = []

    for comment in comments:
        clean_comment = preprocess_text(comment)
        phrases = split_into_phrases(clean_comment)
        all_phrases.extend(phrases)

    if not all_phrases:
        return {
            "aspect_analysis":         [],
            "without_aspect_analysis": [],
        }

    predictions = predict_batch_roberta(all_phrases)

    for phrase, prediction in zip(all_phrases, predictions):
        aspects = extract_aspects(phrase, active_aspects)

        if aspects:
            for aspect in aspects:
                aspect_results.append({
                    "phrase": phrase,
                    "aspect": aspect,
                    "label":  prediction["label"],
                    "score":  prediction["score"],
                })
        else:
            without_aspect_results.append({
                "phrase": phrase,
                "label":  prediction["label"],
                "score":  prediction["score"],
            })

    return {
        "aspect_analysis":         aspect_results,
        "without_aspect_analysis": without_aspect_results,
    }


# DeBERTa ABSA pipeline

def _predict_comments_absa(comments: list[str], active_aspects: list[str]) -> dict:
    aspect_results         = []
    without_aspect_results = []

    all_phrases = []
    for comment in comments:
        clean_comment = preprocess_text(comment)
        phrases = split_into_phrases(clean_comment)
        all_phrases.extend(phrases)

    if not all_phrases:
        return {
            "aspect_analysis":         [],
            "without_aspect_analysis": [],
        }

    phrase_aspect_pairs     = []
    phrases_without_aspects = []

    for phrase in all_phrases:
        aspects = extract_aspects(phrase, active_aspects)
        if aspects:
            for aspect in aspects:
                phrase_aspect_pairs.append({
                    "text":   phrase,
                    "aspect": aspect,
                })
        else:
            phrases_without_aspects.append(phrase)

    if phrase_aspect_pairs:
        predictions = predict_batch_absa(phrase_aspect_pairs)

        for pair, prediction in zip(phrase_aspect_pairs, predictions):
            aspect_results.append({
                "phrase": pair["text"],
                "aspect": pair["aspect"],
                "label":  prediction["label"],
                "score":  prediction["score"],
            })

    if phrases_without_aspects:
        fallback_pairs = [
            {"text": phrase, "aspect": "general"}
            for phrase in phrases_without_aspects
        ]
        fallback_preds = predict_batch_absa(fallback_pairs)

        for phrase, prediction in zip(phrases_without_aspects, fallback_preds):
            without_aspect_results.append({
                "phrase": phrase,
                "label":  prediction["label"],
                "score":  prediction["score"],
            })

    return {
        "aspect_analysis":         aspect_results,
        "without_aspect_analysis": without_aspect_results,
    }



# Full pipline to accept both models without changing analysis_service call
def predict_comments(comments: list[str], active_aspects: list[str]) -> dict:
    if model_state["backend"] == "deberta_absa":
        return _predict_comments_absa(comments, active_aspects)
    else:
        return _predict_comments_roberta(comments, active_aspects)

