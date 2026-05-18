from transformers import AutoTokenizer, AutoModelForSequenceClassification
from core.config import MODEL_NAME

# Fixed labels for cardiffnlp/twitter-roberta-base-sentiment.
# Source: https://github.com/cardiffnlp/tweeteval/blob/main/datasets/sentiment/mapping.txt
LABELS = ["negative", "neutral", "positive"]


def load_sentiment_model(model_name: str = MODEL_NAME):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    model.eval()

    return tokenizer, model