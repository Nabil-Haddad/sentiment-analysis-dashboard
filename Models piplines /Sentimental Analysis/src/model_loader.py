from transformers import AutoTokenizer, AutoModelForSequenceClassification
import urllib.request
import csv

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
TASK = "sentiment"


def get_labels(task: str = TASK):
    labels = []

    mapping_link = (
        f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/"
        f"datasets/{task}/mapping.txt"
    )

    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode("utf-8").split("\n")
        csvreader = csv.reader(html, delimiter="\t")

        labels = [row[1] for row in csvreader if len(row) > 1]

    return labels


def load_sentiment_model(model_name: str = MODEL_NAME):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    model.eval()

    return tokenizer, model