"""
Evaluates the current cardiffnlp/twitter-roberta-base-sentiment model
on the SemEval-2014 restaurant ABSA test set.

Purpose:
    Establish a performance baseline before fine-tuning DeBERTa.
    Every metric recorded here is the number the fine-tuned model must beat.

Results are saved to:
    Models piplines /Sentimental Analysis/reports/baseline_metrics.json
"""

import json
import os
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)
from data_preprocessing import load_absa_dataset, LABEL_REMAP, ID2LABEL


# Constants

CARDIFFNLP_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
BATCH_SIZE       = 32
MAX_LENGTH       = 128


CARDIFF_LABEL_MAP = {
    "LABEL_0": 0,
    "LABEL_1": 1,
    "LABEL_2": 2,
}


# Dataset for baseline

class BaselineDataset(torch.utils.data.Dataset):

    def __init__(self, hf_split, tokenizer):
        self.data      = hf_split
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]

        encoding = self.tokenizer(
            sample["text"],
            max_length=MAX_LENGTH,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids":      encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label":          torch.tensor(LABEL_REMAP[sample["label"]], dtype=torch.long),
        }


# Evaluation function

def evaluate_baseline() -> dict:

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Loading {CARDIFFNLP_MODEL}...")

    tokenizer = AutoTokenizer.from_pretrained(CARDIFFNLP_MODEL)
    model     = AutoModelForSequenceClassification.from_pretrained(CARDIFFNLP_MODEL)
    model.to(device)
    model.eval()

    # Load test split
    _, test_split = load_absa_dataset()
    dataset       = BaselineDataset(test_split, tokenizer)
    dataloader    = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False,
                               num_workers=0)

    print(f"Running inference on {len(dataset)} test examples...")

    all_preds  = []
    all_labels = []

    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)

            # argmax over logits gives the predicted class index
            preds = torch.argmax(outputs.logits, dim=-1).cpu().numpy()

            all_preds.extend(preds)
            all_labels.extend(batch["label"].numpy())

            if (batch_idx + 1) % 5 == 0:
                print(f"  Processed {(batch_idx + 1) * BATCH_SIZE} / {len(dataset)}")

    # Compute metrics
    metrics = {
        "model":     CARDIFFNLP_MODEL,
        "accuracy":  round(accuracy_score(all_labels, all_preds), 4),
        "precision": round(precision_score(all_labels, all_preds, average="macro", zero_division=0), 4),
        "recall":    round(recall_score(all_labels, all_preds, average="macro", zero_division=0), 4),
        "macro_f1":  round(f1_score(all_labels, all_preds, average="macro", zero_division=0), 4),
    }

    # Print results
    print("\n" + "=" * 50)
    print("BASELINE METRICS — cardiffnlp/twitter-roberta")
    print("=" * 50)
    for k, v in metrics.items():
        if k != "model":
            print(f"  {k:<12}: {v}")

    print("\nPer-class breakdown:")
    print(classification_report(
        all_labels, all_preds,
        target_names=["negative", "neutral", "positive"],
        digits=4,
    ))

    # Save results
    reports_dir = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "reports", "Metrics"
    )
    
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "baseline_metrics.json")

    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nSaved to {output_path}")
    return metrics



if __name__ == "__main__":
    evaluate_baseline()