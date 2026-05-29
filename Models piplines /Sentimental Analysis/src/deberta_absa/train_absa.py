import os
import sys
import json
import numpy as np
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, random_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

sys.path.append(os.path.dirname(__file__))
from data_preprocessing import load_absa_dataset, ABSADataset, CLASS_WEIGHTS, ID2LABEL, LABEL2ID


# Hyperparameters
# Every value here was decided based on the ivistigations in the notebook 05.

MODEL_NAME   = "microsoft/deberta-v3-base"
NUM_LABELS   = 3
MAX_LENGTH   = 128   
BATCH_SIZE   = 16     
GRAD_ACCUM   = 2      
EPOCHS       = 5      
LR           = 2e-5   
WARMUP_RATIO = 0.1    
VAL_SPLIT    = 0.1    
SEED         = 42
PATIENCE     = 2     

SCRIPT_DIR  = os.path.dirname(__file__)
MODEL_DIR   = os.path.join(SCRIPT_DIR, "..", "..", "models", "deberta-absa")
REPORTS_DIR = os.path.join(SCRIPT_DIR, "..", "..", "reports", "Metrics")


# Reproducibility
def set_seed(seed: int):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# Evaluation function

def evaluate(model, dataloader, device, class_weights) -> dict:
    model.eval()
    all_preds  = []
    all_labels = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds   = torch.argmax(outputs.logits, dim=-1).cpu().numpy()

            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())

    return {
        "accuracy": round(accuracy_score(all_labels, all_preds), 4),
        "macro_f1": round(f1_score(all_labels, all_preds,
                                   average="macro", zero_division=0), 4),
    }


# Main training function

def train():
    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    print("Loading dataset...")
    train_split, test_split = load_absa_dataset()

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Wrap HuggingFace splits in our PyTorch Dataset
    full_train_dataset = ABSADataset(train_split, tokenizer, MAX_LENGTH)
    test_dataset       = ABSADataset(test_split,  tokenizer, MAX_LENGTH)

    val_size   = int(len(full_train_dataset) * VAL_SPLIT)
    train_size = len(full_train_dataset) - val_size

    train_dataset, val_dataset = random_split(
        full_train_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(SEED),
    )

    print(f"Train: {train_size} | Val: {val_size} | Test: {len(test_dataset)}")

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                              shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE * 2,
                              shuffle=False, num_workers=0)
    test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE * 2,
                              shuffle=False, num_workers=0)

 
    print(f"Loading {MODEL_NAME}...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        torch_dtype=torch.float32,
    )
    model.to(device)

    loss_fn = torch.nn.CrossEntropyLoss(
    weight=CLASS_WEIGHTS.to(device=device, dtype=torch.float32)
    )

    # Optimiser
    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)

    total_steps  = (len(train_loader) // GRAD_ACCUM) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)

    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )

    # Training loop
    best_val_f1    = 0.0
    patience_count = 0
    training_log   = []

    os.makedirs(MODEL_DIR,   exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("\nStarting training...")
    print(f"Epochs: {EPOCHS} | Batch: {BATCH_SIZE} | Grad accum: {GRAD_ACCUM} | LR: {LR}")
    print("-" * 60)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        optimizer.zero_grad()

        for step, batch in enumerate(train_loader, 1):
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss    = loss_fn(outputs.logits, labels)
            loss = loss / GRAD_ACCUM
            loss.backward()

            total_loss += loss.item() * GRAD_ACCUM

            if step % GRAD_ACCUM == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        avg_loss    = total_loss / len(train_loader)
        val_metrics = evaluate(model, val_loader, device, CLASS_WEIGHTS)

        print(
            f"Epoch {epoch}/{EPOCHS} | "
            f"loss: {avg_loss:.4f} | "
            f"val_acc: {val_metrics['accuracy']} | "
            f"val_f1: {val_metrics['macro_f1']}"
        )

        training_log.append({
            "epoch":    epoch,
            "loss":     round(avg_loss, 4),
            "val_acc":  val_metrics["accuracy"],
            "val_f1":   val_metrics["macro_f1"],
        })

        # Early stopping + checkpoint 
        if val_metrics["macro_f1"] > best_val_f1:
            best_val_f1    = val_metrics["macro_f1"]
            patience_count = 0
            model.save_pretrained(MODEL_DIR)
            tokenizer.save_pretrained(MODEL_DIR)
            print(f"  ✓ Best model saved (val_f1={best_val_f1})")
        else:
            patience_count += 1
            print(f"  No improvement ({patience_count}/{PATIENCE})")
            if patience_count >= PATIENCE:
                print(f"  Early stopping at epoch {epoch}")
                break

    # Test evaluation ──────────────────────────────────────────────────
    print("\nLoading best checkpoint for final test evaluation...")
    best_model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    best_model.to(device)

    all_preds  = []
    all_labels = []

    best_model.eval()
    with torch.no_grad():
        for batch in test_loader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            outputs        = best_model(input_ids=input_ids,
                                        attention_mask=attention_mask)
            preds          = torch.argmax(outputs.logits, dim=-1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(batch["labels"].numpy())

    test_metrics = {
        "model":     MODEL_NAME,
        "accuracy":  round(accuracy_score(all_labels, all_preds), 4),
        "precision": round(precision_score(all_labels, all_preds,
                                           average="macro", zero_division=0), 4),
        "recall":    round(recall_score(all_labels, all_preds,
                                        average="macro", zero_division=0), 4),
        "macro_f1":  round(f1_score(all_labels, all_preds,
                                    average="macro", zero_division=0), 4),
    }

    print("\n" + "=" * 50)
    print("FINE-TUNED MODEL — TEST METRICS")
    print("=" * 50)
    for k, v in test_metrics.items():
        if k != "model":
            print(f"  {k:<12}: {v}")

    print("\nPer-class breakdown:")
    print(classification_report(
        all_labels, all_preds,
        target_names=["negative", "neutral", "positive"],
        digits=4,
    ))

    # Save results 
    results = {
        "model":        MODEL_NAME,
        "model_path":   os.path.abspath(MODEL_DIR),
        "training_log": training_log,
        "test_metrics": test_metrics,
    }

    output_path = os.path.join(REPORTS_DIR, "finetuned_metrics.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {output_path}")
    return test_metrics


if __name__ == "__main__":
    train()