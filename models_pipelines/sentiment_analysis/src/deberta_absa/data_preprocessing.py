from datasets import load_dataset
from torch.utils.data import Dataset
import torch
from transformers import AutoTokenizer

# Label mapping
LABEL_REMAP = {-1: 0, 0: 1, 1: 2}
ID2LABEL    = {0: "negative", 1: "neutral", 2: "positive"}
LABEL2ID    = {"negative": 0, "neutral": 1, "positive": 2}


# Class weights
CLASS_WEIGHTS = torch.tensor([1.4903, 1.8880, 0.5558], dtype=torch.float)


# Input format 
def build_absa_input(text: str, aspect: str) -> str:
    return f"aspect: {aspect} [SEP] {text}"


# Dataset class 
class ABSADataset(Dataset):
    def __init__(self, hf_split, tokenizer, max_length: int = 128):
        self.data       = hf_split
        self.tokenizer  = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]

        # Format the input with aspect prefix
        input_text = build_absa_input(sample["text"], sample["aspect"])

        # We need to have the same shape, which is required by the DataLoader
        encoding = self.tokenizer(
            input_text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # Remap raw label from (-1/0/1) to (0/1/2)
        label = LABEL_REMAP[sample["label"]]

        return {
            "input_ids":      encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels":         torch.tensor(label, dtype=torch.long),
        }


# Data loading function 
def load_absa_dataset():
    dataset = load_dataset("yqzheng/semeval2014_restaurants")
    return dataset["train"], dataset["test"]


if __name__ == "__main__":

    print("Loading dataset...")
    train_split, test_split = load_absa_dataset()

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")

    train_dataset = ABSADataset(train_split, tokenizer)
    test_dataset  = ABSADataset(test_split,  tokenizer)

    print(f"Train size: {len(train_dataset)}")
    print(f"Test size: {len(test_dataset)}")

    # Inspect first item to confirm shapes and values are correct
    item = train_dataset[0]
    print(f"\nFirst item:")
    print(f"input_ids shape: {item['input_ids'].shape}")
    print(f"attention_mask shape: {item['attention_mask'].shape}")
    print(f"label: {item['labels'].item()} ({ID2LABEL[item['labels'].item()]})")

    # Decode the input back to text to verify the format is correct
    decoded = tokenizer.decode(item["input_ids"], skip_special_tokens=False)
    print(f"decoded input: {decoded[:120]}...")