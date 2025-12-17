from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments

MODEL_NAME = "google/flan-t5-small"

dataset = load_dataset("json", data_files="data/commands.json")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def preprocess(example):
    prompt = "Translate English to canonical command: " + example["input"]
    inputs = tokenizer(prompt, padding="max_length", truncation=True, max_length=128)
    labels = tokenizer(example["output"], padding="max_length", truncation=True, max_length=64)
    inputs["labels"] = labels["input_ids"]
    return inputs

tokenized = dataset["train"].map(preprocess)

args = TrainingArguments(
    output_dir="model",
    num_train_epochs=10,          
    per_device_train_batch_size=16,
    fp16=True,                    
    learning_rate=3e-4,
    report_to="none"
)


trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
    tokenizer=tokenizer
)

trainer.train()

model.save_pretrained("model")
tokenizer.save_pretrained("model")
