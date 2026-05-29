import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from core.config import MODEL_NAME, ABSA_MODEL_PATH

LABELS = ["negative", "neutral", "positive"]

# Load roberta model and tokenizer
def load_sentiment_model(model_name: str = MODEL_NAME):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model     = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    return tokenizer, model


# Load fune_tuned Deberta absa model and tokenizer
def load_absa_model():

    # Resolve file path's issues
    base_dir   = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.normpath(os.path.join(base_dir, "..", "..", ABSA_MODEL_PATH))

    if not os.path.exists(model_path):
        model_path = ABSA_MODEL_PATH

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"ABSA model checkpoint not found at '{model_path}'.\n"
            f"Run train_absa.py first to generate the fine-tuned model."
        )

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path, torch_dtype=torch.float32,)
    model.eval()
    return tokenizer, model